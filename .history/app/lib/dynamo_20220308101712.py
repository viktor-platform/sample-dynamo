import json
from io import BytesIO
from pathlib import Path
import re
from typing import Dict, List
from xml.etree import ElementTree as ET

import trimesh

import base64
import struct

from viktor.geometry import Group, _Mesh
from viktor.views import DataItem


class InvalidDynamoFile(KeyError):
    def __init__(self):
        super().__init__("Invalid Dynamo Script format. File should contain 'Inputs', which should contain 'Name' and "
                         "'Id', and 'Nodes', which should contain 'Id' and 'InputValue'")


class InvalidMapping(KeyError):
    def __init__(self, param_mapping: str):
        super().__init__(f"Invalid mapping of parametrization to Dynamo inputs. No input with name '{param_mapping}'"
                         f" found ")


class UnknownDynamoInputType(ValueError):
    def __init__(self, dynamo_type: str):
        super().__init__(f"Input of type '{dynamo_type}' unknown. Add to code or adjust input.")


def update_dynamo_input_values(dynamo: dict, input_mapping: dict) -> dict:
    """
    Update the input values of a Dynamo file contents.
    :param dynamo: the dynamo file contents.
    :param input_mapping: key should be the name of the Dynamo input node, value the value to be set.
    """
    try:
        dyn_input_names = {dyn_input["Name"]: dyn_input["Id"] for dyn_input in dynamo["Inputs"]}
        dyn_nodes = {node["Id"]: node for node in dynamo["Nodes"]}
    except KeyError:
        raise InvalidDynamoFile()

    for input, value in input_mapping.items():
        if input not in dyn_input_names:
            raise InvalidMapping(input)
        try:
            dyn_nodes[dyn_input_names[input]]["InputValue"] = value
        except KeyError:
            raise InvalidDynamoFile()
    return dynamo


def parametrize_dynamo(dynamo: dict, linebreaks: bool = True) -> str:
    """
    Parse the input nodes of a Dynamo file into a VIKTOR parametrization.
    :param dynamo: the dynamo file contents.
    :param linebreaks: if set to true, adds a linebreak between every input and sets the flex to 90.
    :return: The VIKTOR parametrization.
    """
    params = []
    imports = {"from viktor.parametrization import Parametrization",
               "from viktor.parametrization import Tab, Section"}
    if not dynamo.get("Inputs"):
        raise InvalidDynamoFile()
    for index, dyn_input in enumerate(dynamo["Inputs"]):
        input_name = dyn_input["Name"]
        if dyn_input["Type"] == "number":
            imports.add("from viktor.parametrization import NumberField")
            field = f'NumberField("{input_name}"'
            if dyn_input.get("MaximumValue"):
                field += f', max={dyn_input["MaximumValue"]}'
                field += f', min={dyn_input["MinimumValue"]}'
                field += f', variant=NumberField.Variant.SLIDER'
                field += f', step={dyn_input["StepValue"]}'
            if dyn_input["NumberType"] == "integer":
                field += f", integer=True"
            if dyn_input["NumberType"] == "integer":
                field += f", integer=True"
            field += f', default={float(dyn_input["Value"])}'
        elif dyn_input["Type"] == "boolean":
            imports.add("from viktor.parametrization import ToggleButton")
            field = f'ToggleButton("{input_name}"'
            if dyn_input['Value'] == "false":
                value = False
            else:
                value = True
            field += f', default={value}'
        elif dyn_input["Type"] == "string":
            imports.add("from viktor.parametrization import TextField")
            field = f'TextField("{input_name}", default="{dyn_input["Value"]}"'
        elif dyn_input["Type"] == "date":
            imports.add("from viktor.parametrization import DateField")
            field = f'DateField("{input_name}", default="{dyn_input["Value"]}"'
        else:
            raise UnknownDynamoInputType(dyn_input["Type"])
        if linebreaks:
            field += ", flex=90)"
        else:
            field += ", flex=90)"

        input_munch_name = re.sub(' +', "_", re.sub('[^A-Za-z0-9 ]+', ' ', input_name)).lower()
        params.append(f"input.dynamo_input.{input_munch_name} = {field}")
        if linebreaks:
            imports.add("from viktor.parametrization import LineBreak")
            params.append(f"input.dynamo_input.linebreak_{index*100} = LineBreak()")

    parametrization = "\n".join(imports)
    parametrization += "\n\n" + "class DynamoParamtrization(Parametrization):\n" \
                                "    input = Tab('Input')\n" \
                                "    input.dynamo_input = Section('Dynamo input')"

    parametrization += "\n    " + "\n    ".join(params)
    return parametrization


def stl_to_mesh(f: BytesIO) -> Group:
    """
    Convert STL file to Viktor GeometryResult containing Mesh objects

    :param f: File handle of STL
    :return:
    """
    scene = trimesh.load(f, file_type="stl")
    objects = []
    for _, mesh in scene.geometry.items():
        objects.append(_Mesh(vertices=mesh.vertices.tolist(), faces=mesh.faces.tolist()))
        objects.append(_Mesh(vertices=mesh.vertices.tolist(),
                             faces=[list(reversed(e)) for e in mesh.faces.tolist()]))  # to visualize the other side
    return Group(objects)

def dynamojson_to_mesh(f: dict):
    array = bytearray(base64.b64decode(mesh["TriangleVertices"]))
    numbers = []
    vertices = []
    for i, v in enumerate(array):
        # numbers are encoded as single precision floating point values in Dynamo. This means that they are represented as 4 bytes, so we can unpack each 4 bytes to a float
        if i % 4 == 0:
            numbers.extend(struct.unpack('f', array[i:i+4]))
            if len(numbers) == 3:
                vertices.append(numbers)
                numbers = []

    # no explicit definition of faces in the export from dynamo. So assume here that vertices are ordered 
    face = []
    faces = []
    for i, v in enumerate(vertices):
        face.append(i)
        if len(face) == 3:
            faces.append(face)
            face = []

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    objects = []
    for _, _mesh in mesh.geometry.items():
        objects.append(_Mesh(vertices=_mesh.vertices.tolist(), faces=_mesh.faces.tolist()))
        objects.append(_Mesh(vertices=_mesh.vertices.tolist(),
                             faces=[list(reversed(e)) for e in _mesh.faces.tolist()]))  # to visualize the other side
    return Group(objects)


def get_output_data(dynamo_output_names: Dict[str, str], dynamo_script: dict, dynamo_output_xml: bytes) -> List[DataItem]:
    output_data = []
    output_xml = ET.fromstring(dynamo_output_xml)
    output_results = {}
    for node in output_xml.find("evaluation0").findall("Node"):
        output_results[node.attrib["guid"].replace("-", "")] = node.find("output0").attrib["value"]

    output_ids = {dyn_output["Name"]: dyn_output["Id"] for dyn_output in dynamo_script["Outputs"]}
    for dynamo_output_name, data_item_label in dynamo_output_names.items():
        output_id = output_ids[dynamo_output_name]
        output_data.append(DataItem(data_item_label, round(float(output_results[output_id]), 2)))
    return output_data


if __name__ == '__main__':
    files_folder = Path(__file__).parent/"files"
    input_file = files_folder/"dynamo_model_sample_app.dyn"
    output_file = files_folder/"parametrization.py"
    dynamo_inputs = json.loads(input_file.read_bytes())
    output_file.write_text(parametrize_dynamo(dynamo_inputs))
