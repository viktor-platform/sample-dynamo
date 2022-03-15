import json
from io import BytesIO
from typing import Tuple

from pathlib import Path
from viktor.errors import ExecutionError

from app.lib.constants import OUTPUT_FILE_NAME, MESH_JSON_NAME
from viktor import UserException
from viktor.external.generic import GenericAnalysis
from viktor.utils import memoize

@memoize
def run_dynamo_script(dynamo_script: dict) -> Tuple[str, str]:
    # change test to True if the dynamo script run should be mocked
    # test = False
    # if test:
    #     # assume the following path for the output file
    #     output_path = Path(__file__).parent.parent / 'residential_block' / 'files' / 'output.xml'
    #     with open(output_path) as output_file:
    #         output_file_string = output_file.read()
    #     # assume the following path for the mesh json file
    #     geometry_path = Path(__file__).parent.parent / 'residential_block' / 'files' / 'mesh.json'
    #     with open(geometry_path) as geometry_file:
    #         geometry_file_string = geometry_file.read()
    #     return geometry_file_string, output_file_string

    # for i in range(5):
    #     print('Trying:', i)
    #     try:
    #         generic_analysis = GenericAnalysis(files=[("script.dyn", BytesIO(json.dumps(dynamo_script).encode()))],
    #                                            executable_key="dynamo",
    #                                            output_filenames=["script.dyn", MESH_JSON_NAME, OUTPUT_FILE_NAME])
    #         generic_analysis.execute(timeout=100)
    #     except TimeoutError:
    #         raise UserException("Dynamo script got a timeout.")
    #     except ConnectionError:
    #         raise UserException("Error: Could not connect to server.")
    #     except ExecutionError:
    #         continue
    #     else:
    #         break
    # else:
    #     raise UserException('Something went wrong during the execution.')

#End tester

    try:
        generic_analysis = GenericAnalysis(files=[("script.dyn", BytesIO(json.dumps(dynamo_script).encode()))],
                                           executable_key="dynamo",
                                           output_filenames=["script.dyn", MESH_JSON_NAME, OUTPUT_FILE_NAME])
        generic_analysis.execute(timeout=30)
    except TimeoutError:
        raise UserException("Dynamo script got a timeout.")
    except ConnectionError:
        raise UserException("Error: Could not connect to server.")

    return (generic_analysis.get_output_file(MESH_JSON_NAME).getvalue().decode(),
            generic_analysis.get_output_file(OUTPUT_FILE_NAME).getvalue().decode())
