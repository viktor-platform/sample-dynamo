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
