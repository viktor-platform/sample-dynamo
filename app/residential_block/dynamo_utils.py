import base64
from io import BytesIO
from typing import List, Dict

from viktor.external.generic import GenericAnalysis
from pathlib import Path

from viktor.utils import memoize
from viktor.views import DataItem
from viktor.core import File
from viktor.external.dynamo import DynamoFile, get_dynamo_result, convert_geometry_to_glb


def json_serialize(file_content: bytes) -> str:
    """Serializes a bytestream into a string using base64 encoding"""
    return base64.b64encode(file_content).decode('utf-8')


def json_deserialize(file_str: str) -> bytes:
    """Deserializes a base64 encoded string back into a bytestream"""
    return base64.b64decode(file_str.encode('utf-8'))


def decode_file(file: File):
    return json_serialize(file.getvalue_binary())


def from_decode_to_file(file: str):
    return File.from_data(json_deserialize(file))


def create_dynamo_file(params) -> DynamoFile:
    """This function converts the parametrization to a dynamo file. The dynamo file is created using an
    existing dynamo script as template, and updating the specified fields with the given parameters."""

    # First the path to the dynamo file is specified and loaded
    file = File.from_path(Path(__file__).parent.parent / "lib" / "files" / "dynamo_model_sample_app.dyn")
    input_file = DynamoFile(file)

    # Update dynamo file with parameters from user input
    input_file.update("Number of houses", params.step_2.number_of_houses)
    input_file.update("Number of floors", params.step_2.number_of_floors)
    input_file.update("Depth", params.step_2.depth)
    input_file.update("Width", params.step_2.width)
    input_file.update("Height floor", params.step_2.height_floor)
    input_file.update("Height roof", params.step_2.height_roof)

    # Generate updated dynamo file and load into memory
    return input_file


@memoize
def run_dynamo(input_file: str) -> Dict[str, str]:
    """ This method collects, updates and then runs the dynamo model. Three output files are generated from the
    dynamo model: the geometry, the numerical output for the Viktor DataView and the numerical output in a dictionary."""
    input_file = from_decode_to_file(input_file)
    files = [('input.dyn', BytesIO(input_file.getvalue_binary()))]

    # Run the analysis and obtain the output file
    generic_analysis = GenericAnalysis(files=files, executable_key="dynamo",
                                       output_filenames=["output.xml", "geometry.json"])
    generic_analysis.execute(timeout=60)

    # Retrieve output files (output.xml and geometry.json)
    output_file = generic_analysis.get_output_file("output.xml", as_file=True)
    geometry_file = generic_analysis.get_output_file('geometry.json', as_file=True)

    # Convert geometry file (json) to glb
    glb_file = convert_geometry_to_glb(geometry_file)

    # In order to memoize an app, input and output needs to be json serializable
    # Therefore, the glb file is decoded.
    glb_file_decoded = decode_file(glb_file)
    output_file_decoded = decode_file(output_file)

    return {
        'glb_file': glb_file_decoded,
        'output_file': output_file_decoded
    }


def get_dynamo_output_results(input_file: DynamoFile, output_file: File) -> dict:
    """This function extracts the output of the Dynamo results by using the input and output files."""
    # Collect ids for the computational output from the dynamo file (numerical output)
    output_id_floor_area = input_file.get_node_id("(OUTPUT) Floor area per house")
    output_id_total_cost = input_file.get_node_id("(OUTPUT) Total cost")
    output_id_MKI = input_file.get_node_id("(OUTPUT) MKI")
    output_id_CO2 = input_file.get_node_id("(OUTPUT) CO2")

    # Create dictionary to store results (numerical output)
    dynamo_output_report = {}

    # Store output files to dictionary (numerical output)
    with output_file.open_binary() as f:
        dynamo_output_report['result_floor_area'] = {'label': "Floor area", 'value': get_dynamo_result(f, id_=output_id_floor_area), 'suffix': "m²"}
        dynamo_output_report['result_total_cost'] = {'label': "Total cost", 'value': get_dynamo_result(f, id_=output_id_total_cost),  'suffix': "€"}
        dynamo_output_report['result_MKI'] = {'label': "MKI", 'value': get_dynamo_result(f, id_=output_id_MKI),  'suffix': ""}
        dynamo_output_report['result_floor_CO2'] = {'label': "CO₂ emission", 'value':get_dynamo_result(f, id_=output_id_CO2),  'suffix': "ton CO₂"}

    return dynamo_output_report


def convert_dynamo_file_to_data_items(input_file: DynamoFile, output_file: File) -> List[DataItem]:
    dynamo_output_results = get_dynamo_output_results(input_file=input_file, output_file=output_file)
    # Convert output files to Viktor DataItems and store them in a list (numerical output)
    dataview_output_items = []
    for key, data_items_args in dynamo_output_results.items():
        dataview_output_items.append(
            DataItem(label=data_items_args['label'],
                     value=round(float(data_items_args['value']), 2),
                     suffix=data_items_args['suffix'])
        )
    return dataview_output_items
