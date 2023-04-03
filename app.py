from typing import Tuple

from viktor import ViktorController
from viktor.parametrization import ViktorParametrization, NumberField
from viktor.views import GeometryAndDataView, GeometryAndDataResult, DataItem, DataGroup
from viktor.external.generic import GenericAnalysis
from viktor.external.dynamo import DynamoFile, convert_geometry_to_glb, get_dynamo_result
from viktor.core import File
from pathlib import Path


class Parametrization(ViktorParametrization):
    # Input fields
    number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=3.0)
    number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
    depth = NumberField("Depth [m]", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
    width = NumberField("Width [m]", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
    height_floor = NumberField("Height floor", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5, suffix='m')
    height_roof = NumberField("Height roof", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5, suffix='m')


class Controller(ViktorController):
    viktor_enforce_field_constraints = True  # Resolves upgrade instruction https://docs.viktor.ai/sdk/upgrades#U83

    label = 'Residential Block'
    parametrization = Parametrization

    @staticmethod
    def update_model(params) -> Tuple[File, DynamoFile]:
        """This method updates the nodes of the dynamo file with the parameters
        from the parametrization class."""

        # First the path to the dynamo file is specified and loaded
        file_path = Path(__file__).parent / "dynamo_model_sample_app.dyn"
        _file = File.from_path(file_path)
        dyn_file = DynamoFile(_file)

        # Update dynamo file with parameters from user input
        dyn_file.update("Number of houses", params.number_of_houses)
        dyn_file.update("Number of floors", params.number_of_floors)
        dyn_file.update("Depth", params.depth)
        dyn_file.update("Width", params.width)
        dyn_file.update("Height floor", params.height_floor)
        dyn_file.update("Height roof", params.height_roof)

        # generate updated file
        input_file = dyn_file.generate()

        return input_file, dyn_file

    @GeometryAndDataView("Building 3D", duration_guess=5)
    def geometry_and_data_view(self, params, **kwargs):
        """The endpoint that initiates the logic to visualize the geometry and data executed
        and retrieved from a Dynamo script."""
        # Step 1: Update model
        input_file, dynamo_file = self.update_model(params)

        # Step 2: Running analyses
        files = [
            ('input.dyn', input_file),
        ]

        generic_analysis = GenericAnalysis(files=files, executable_key="dynamo",
                                           output_filenames=["output.xml", "geometry.json"])
        generic_analysis.execute(timeout=60)

        # Step 3: Processing geometry
        geometry_file = generic_analysis.get_output_file('geometry.json', as_file=True)
        glb_file = convert_geometry_to_glb(geometry_file)

        # Step 4: Process numerical output
        output_file = generic_analysis.get_output_file('output.xml', as_file=True)
        data_group = self.convert_dynamo_file_to_data_items(dynamo_file, output_file)

        return GeometryAndDataResult(geometry=glb_file, data=data_group)

    @staticmethod
    def convert_dynamo_file_to_data_items(input_file: DynamoFile, output_file: File) -> DataGroup:
        """Extracts the output of the Dynamo results by using the input and output files."""
        # Collect ids for the computational output from the dynamo file (numerical output)
        output_id_floor_area = input_file.get_node_id("(OUTPUT) Floor area per house")
        output_id_total_cost = input_file.get_node_id("(OUTPUT) Total cost")
        output_id_mki = input_file.get_node_id("(OUTPUT) MKI")
        output_id_co2 = input_file.get_node_id("(OUTPUT) CO2")

        # Collect the numerical results from the output file using the collected ids
        with output_file.open_binary() as f:
            floor_area = get_dynamo_result(f, id_=output_id_floor_area)
            total_cost = get_dynamo_result(f, id_=output_id_total_cost)
            mki = get_dynamo_result(f, id_=output_id_mki)
            co2 = get_dynamo_result(f, id_=output_id_co2)

        # Add values to a structured data group
        data_group = DataGroup(
            DataItem(label="Floor area", value=round(float(floor_area), 2), suffix="m²"),
            DataItem(label="Total cost", value=round(float(total_cost), 2), suffix="€"),
            DataItem(label="MKI", value=round(float(mki), 2)),
            DataItem(label="CO₂ emission", value=round(float(co2), 2), suffix="ton CO₂"),
        )
        return data_group
