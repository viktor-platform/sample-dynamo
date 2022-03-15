
from pathlib import Path
import json

from viktor.api_v1 import API
from viktor.core import ViktorController
from viktor.views import Summary, DataGroup, DataView, DataResult, DataItem, GeometryAndDataView, GeometryAndDataResult
from viktor.views import MapView, MapPoint, MapPolyline, MapPolygon, MapResult, MapLine
from viktor.parametrization import GeoPoint
from .parametrization import ResidentialBlockParametrization
from io import BytesIO
from munch import Munch

from ..lib.worker import run_dynamo_script
from ..lib.dynamo import stl_to_mesh, update_dynamo_input_values, get_output_data, dynamojson_to_mesh


# class InvalidDynamoFile(KeyError):
#     def __init__(self):
#         super().__init__("Invalid Dynamo Script format. File should contain 'Inputs', which should contain 'Name' and "
#                          "'Id', and 'Nodes', which should contain 'Id' and 'InputValue'")


# class InvalidMapping(KeyError):
#     def __init__(self, param_mapping: str):
#         super().__init__(f"Invalid mapping of parametrization to Dynamo inputs. No input with name '{param_mapping}'"
#                          f" found ")


# class UnknownDynamoInputType(ValueError):
#     def __init__(self, dynamo_type: str):
#         super().__init__(f"Input of type '{dynamo_type}' unknown. Add to code or adjust input.")

class ResidentialBlockController(ViktorController):
	parametrization = ResidentialBlockParametrization
	summary = Summary()
	label = "ResidentialBlock"
	children = []
	show_children_as = None
	viktor_convert_entity_field = True

	@GeometryAndDataView("Building", duration_guess=5)
	def geometry_and_data_view(self, params, **kwargs):
		mapped_params = self._map_params_to_dynamo_inputs(params)
		dynamo_script_file = Path(__file__).parent.parent/"lib"/"files"/"dynamo_model_sample_app.dyn"
		dynamo_script = json.loads(dynamo_script_file.read_bytes())
		updated_dynamo_script = update_dynamo_input_values(dynamo_script, mapped_params)

		mesh_json_output, data_output = run_dynamo_script(updated_dynamo_script)		
		mesh_dict = json.loads(mesh_json_output)

		dynamo_output_for_dataitem = {"(OUTPUT) Floor area per house": "Floor area per house [m2]",
		"(OUTPUT) Total cost": "Total project cost [€]",
		"(OUTPUT) MKI": "MKI [€]",
		"(OUTPUT) CO2": "CO2 emission [kg NOx]"
		}
		data_items = get_output_data(dynamo_output_for_dataitem, dynamo_script, data_output.encode())
		geometry_group = dynamojson_to_mesh(mesh_dict)

		return GeometryAndDataResult(data=DataGroup(*data_items), visualization_group=geometry_group)

	@staticmethod
	def _map_params_to_dynamo_inputs(params):
		"""Return a dictionary with the input note name as keys with the subsequent parameter values"""

		return {
			"Number of houses": params.tab1.section1.number_of_houses,
			"Number of floors": params.tab1.section1.number_of_floors,
			"Depth": params.tab1.section1.depth,
			"Width": params.tab1.section1.width,
			"Height floor": params.tab1.section1.height_floor,
			"Height roof": params.tab1.section1.height_roof,
		}

	@MapView('Map view', duration_guess=1)  # in seconds, if it is larger or equal to 3, the "update" button will appear
	def get_map_view(self, params: Munch, **kwargs) -> MapResult:
		features = []

		# if params.tab1.section2.point:
		# 	marker = params.tab1.section2.point
		# 	features.append(MapPoint.from_geo_point(marker))

		if params.tab1.section2.line:
			marker = params.tab1.section2.line
			coords_residential = []
			for point in marker.points:
				# print(type(point))
				coords_residential.append(point.rd)
				moved_y = point.rd[0]+6
				moved_x = point.rd[1]+6
				moved_x_y = (moved_y,moved_x)
				print(moved_x_y)
				# print(point.rd[1])
				# point_tuple = {point}
				# print(point_tuple)
			print(coords_residential)
			print(type(coords_residential[0]))
			features.append(MapPolyline.from_geo_polyline(marker))

		# if params.tab1.section2.polygon:
		# 	marker = params.tab1.section2.polygon
		# 	features.append(MapPolygon.from_geo_polygon(marker))

		return MapResult(features)