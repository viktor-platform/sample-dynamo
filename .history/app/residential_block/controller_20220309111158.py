
from pathlib import Path
import json
import matplotlib
from matplotlib import patches

from matplotlib.patches import Rectangle
from matplotlib.pyplot import yticks

from viktor.api_v1 import API
from viktor.core import ViktorController
from viktor.views import Summary, DataGroup, DataView, DataResult, DataItem, GeometryAndDataView, GeometryAndDataResult
from viktor.views import MapView, MapPoint, MapPolyline, MapPolygon, MapResult, MapLine
from viktor.parametrization import GeoPoint
from viktor.geometry import RDWGSConverter
import numpy as np
from math import cos, sin, sqrt
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
			coords = []
			for point in marker.points:
				coords_residential = []
				for property, value in vars(point).items():
					# print(value)
					coords_residential.append(value)
				coords.append(point.rd[0])
				coords.append(point.rd[1])


				# print(point[0])
				moved_y = point.rd[0]+6
				moved_x = point.rd[1]+6
				moved_y_wgs, moved_x_wgs = RDWGSConverter.from_rd_to_wgs((moved_y, moved_x))
				# features.append(MapPoint(moved_y_wgs, moved_x_wgs))
				features.append(MapPoint(coords_residential[0], coords_residential[1]))
				# features.append(MapPoint(GeoPoint((point[0],point[1]))))
				# features.append(MapPoint(GeoPoint.from_rd((moved_y,moved_x))))

				# moved_x_y = (moved_y,moved_x)
				coords_residential.append(GeoPoint.from_rd((moved_y,moved_x)))
				lat, lon = RDWGSConverter.from_rd_to_wgs((100000, 400000))
				# coords_residential.append(moved_x_y)
				# print(point.rd[1])
				# point_tuple = {point}
				# print(point_tuple)

			# Phi = 90
			# h=6
			w=3
			cx = point.rd[0]
			cy = point.rd[1]

			h = sqrt( (coords[2] - coords[0])**2 + (coords[3] - coords[1])**2 )
			Phi = abs((coords[3]-coords[1])/(coords[2]-coords[0]))
			print(Phi)


			x = cx + w * cos(Phi) - h * sin(Phi)
			y = cy + w * sin(Phi) + h * cos(Phi)


			transformed_x_wgs, transformed_y_wgs = RDWGSConverter.from_rd_to_wgs((x, y))
			features.append(MapPoint(transformed_x_wgs, transformed_y_wgs))

			# print(cx, "transformerd to: ", x)
			# print(cy, "transformerd to: ", y)
			# center(1,1) = (center_x,center_y)
			center_x = 100000
			center_y = 400000
			angle        = 90
			height       = 8
			width        = 6      

			center_x_wgs, center_y_wgs = RDWGSConverter.from_rd_to_wgs((center_x, center_y))
			features.append(MapPoint(center_x_wgs, center_y_wgs))


			#TOP RIGHT VERTEX:
			Top_Right_x = center_x + ((width / 2) * cos(angle)) - ((height / 2) * sin(angle))
			Top_Right_y = center_y + ((width / 2) * sin(angle)) + ((height / 2) * cos(angle))
			# transformed_x_wgs, transformed_y_wgs = RDWGSConverter.from_rd_to_wgs((center_x, center_y))
			Top_Right_x_wgs, Top_Right_y_wgs = RDWGSConverter.from_rd_to_wgs((Top_Right_x, Top_Right_y))
			features.append(MapPoint(Top_Right_x_wgs, Top_Right_y_wgs))

			#TOP LEFT VERTEX:
			Top_Left_x = center_x - ((width / 2) * cos(angle)) - ((height / 2) * sin(angle))
			Top_Left_y = center_y - ((width / 2) * sin(angle)) + ((height / 2) * cos(angle))
			Top_Left_x_wgs, Top_Left_y_wgs = RDWGSConverter.from_rd_to_wgs((Top_Left_x, Top_Left_y))
			features.append(MapPoint(Top_Left_x_wgs, Top_Left_y_wgs))


			#BOTTOM LEFT VERTEX:
			Bot_Left_x = center_x - ((width / 2) * cos(angle)) + ((height / 2) * sin(angle))
			Bot_Left_y = center_y - ((width / 2) * sin(angle)) - ((height / 2) * cos(angle))
			Bot_Left_x_wgs, Bot_Left_y_wgs = RDWGSConverter.from_rd_to_wgs((Bot_Left_x, Bot_Left_y))
			features.append(MapPoint(Bot_Left_x_wgs, Bot_Left_y_wgs))


			#BOTTOM RIGHT VERTEX:
			Bot_Right_x = center_x + ((width / 2) * cos(angle)) + ((height / 2) * sin(angle))
			Bot_Right_y = center_y + ((width / 2) * sin(angle)) - ((height / 2) * cos(angle))
			Bot_Right_x_wgs, Bot_Right_y_wgs = RDWGSConverter.from_rd_to_wgs((Bot_Right_x, Bot_Right_y))
			features.append(MapPoint(Bot_Right_x_wgs, Bot_Right_y_wgs))
		

		# print(coords_residential)
			
			# features.append(MapPoint(coords_residential))
			features.append(MapPolyline.from_geo_polyline(marker))
			# features.append(MapPolygon(coords_residential))

		# if params.tab1.section2.polygon:
		# 	marker = params.tab1.section2.polygon
		# 	features.append(MapPolygon.from_geo_polygon(marker))

		return MapResult(features)