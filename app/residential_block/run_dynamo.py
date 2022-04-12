from io import BytesIO
from viktor.external.generic import GenericAnalysis
from pathlib import Path

from viktor.utils import memoize
from viktor.views import DataItem
from viktor.core import File
from viktor.external.dynamo import DynamoFile, get_dynamo_result, convert_geometry_to_glb


# @memoize
def run_dynamo(params):
    """ This method collects, updates and then runs the dynamo model. Three output files are generated from the
    dynamo model: the geometry, the numerical output for the Viktor DataView and the numerical output in a dictionary."""

    # First the path to the dynamo file is specified and loaded
    file = File.from_path(Path(__file__).parent.parent / "lib" / "files" / "dynamo_model_sample_app.dyn")
    input_file = DynamoFile(file)

    # Collect ids for the computational output from the dynamo file (numerical output)
    output_id_floor_area = input_file.get_node_id("(OUTPUT) Floor area per house")
    output_id_total_cost = input_file.get_node_id("(OUTPUT) Total cost")
    output_id_MKI = input_file.get_node_id("(OUTPUT) MKI")
    output_id_CO2 = input_file.get_node_id("(OUTPUT) CO2")

    # Update dynamo file with parameters from user input
    input_file.update("Number of houses", params.step_2.number_of_houses)
    input_file.update("Number of floors", params.step_2.number_of_floors)
    input_file.update("Depth", params.step_2.depth)
    input_file.update("Width", params.step_2.width)
    input_file.update("Height floor", params.step_2.height_floor)
    input_file.update("Height roof", params.step_2.height_roof)

    # Generate updated dynamo file and load into memory
    input_file = input_file.generate()
    files = [('input.dyn', BytesIO(input_file.getvalue_binary()))]

    # Run the analysis and obtain the output file
    generic_analysis = GenericAnalysis(files=files, executable_key="dynamo",
                                       output_filenames=["output.xml", "geometry.json"])
    generic_analysis.execute(timeout=60)

    # Generate output file and set up data for the DataViewer
    output_file = generic_analysis.get_output_file("output.xml", as_file=True)

    # Create list and dictionary to store results (numerical output)
    dynamo_output_report = {}
    dataview_output_items = []

    # Store output files to dictionary (numerical output)
    with output_file.open_binary() as f:
        dynamo_output_report['result_floor_area'] = [get_dynamo_result(f, id_=output_id_floor_area),
                                                     "Floor area [m2]"]
        dynamo_output_report['result_total_cost'] = [get_dynamo_result(f, id_=output_id_total_cost),
                                                     "Total cost €"]
        dynamo_output_report['result_MKI'] = [get_dynamo_result(f, id_=output_id_MKI), "MKI"]
        dynamo_output_report['result_floor_CO2'] = [get_dynamo_result(f, id_=output_id_CO2), "CO2 emission"]

    # Convert output files to Viktor DataItems and store them in a list (numerical output)
    for key in dynamo_output_report.keys():
        dataview_output_items.append(
            DataItem(dynamo_output_report[key][1], round(float(dynamo_output_report[key][0]), 2)))

    # Create and convert geometry
    geometry_file = generic_analysis.get_output_file('geometry.json', as_file=True)
    glb_file = convert_geometry_to_glb(geometry_file)

    return glb_file, dataview_output_items, dynamo_output_report
