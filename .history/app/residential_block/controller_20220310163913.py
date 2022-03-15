
from pathlib import Path
import json
from typing import Tuple

from viktor.core import ViktorController, progress_message
from viktor.views import Summary, DataGroup, GeometryAndDataView, GeometryAndDataResult, DataView
from viktor.views import MapView, MapPoint,  MapPolygon, MapResult, SummaryItem
from viktor.geometry import RDWGSConverter
from viktor.result import ViktorResult
from viktor import UserException
from math import cos, sin, pi
from munch import Munch

from pathlib import Path
from viktor.result import DownloadResult
from viktor.external.spreadsheet import DirectInputCell, NamedInputCell, render_spreadsheet
from viktor.external.word import WordFileTag, WordFileImage, render_word_file
from viktor.views import DataItem


from .parametrization import ResidentialBlockParametrization
from ..lib.worker import run_dynamo_script
from ..lib.dynamo import update_dynamo_input_values, get_output_data, dynamojson_to_mesh

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

class ResidentialBlockController(ViktorController):
    parametrization = ResidentialBlockParametrization
    summary = Summary()
    label = "ResidentialBlock"
    children = []
    show_children_as = None
    viktor_convert_entity_field = True

    def run_dynamo(self, params) -> Tuple[dict, list]:
        mapped_params = self._map_params_to_dynamo_inputs(params)
        dynamo_script_file = Path(__file__).parent.parent/"lib"/"files"/"dynamo_model_sample_app.dyn"
        dynamo_script = json.loads(dynamo_script_file.read_bytes())
        updated_dynamo_script = update_dynamo_input_values(dynamo_script, mapped_params)

        mesh_json_output, data_output = run_dynamo_script(updated_dynamo_script)		
        mesh_dict = json.loads(mesh_json_output)

        dynamo_output_for_dataitem = [
            "(OUTPUT) Floor area per house",
            "(OUTPUT) Total cost",
            "(OUTPUT) MKI",
            "(OUTPUT) CO2"
        ]
        data_output = get_output_data(dynamo_output_for_dataitem, dynamo_script, data_output.encode())
        geometry_group = dynamojson_to_mesh(mesh_dict)
        return data_output, geometry_group

    @GeometryAndDataView("Building 3D", duration_guess=5)
    def geometry_and_data_view(self, params, **kwargs):
        if params.step_2.number_of_houses>params.step_1.number_of_houses:
            raise UserException("Number of houses is larger than provided in step 1! Please go back to step 1 and increase the number of houses.")

        if params.step_2.width>params.step_1.width:
            raise UserException("The width is larger than provided in step 1! Please go back to step 1 and increase the width.")

        if params.step_2.depth>params.step_1.depth:
            raise UserException("The depth is larger than provided in step 1! Please go back to step 1 and increase the depth.")

        data_output, geometry_group = self.run_dynamo(params)

        dynamo_output_for_dataitem = {
            "(OUTPUT) Floor area per house": "Floor area per house [m2]",
            "(OUTPUT) Total cost": "Total project cost [€]",
            "(OUTPUT) MKI": "MKI [€]",
            "(OUTPUT) CO2": "CO2 emission [kg NOx]"
        }
        output_data_items = []
        for dynamo_output_name, data_item_label in dynamo_output_for_dataitem.items():
            output_data_items.append(DataItem(data_item_label, round(float(data_output[dynamo_output_name]), 2)))

        return GeometryAndDataResult(data=DataGroup(*output_data_items), visualization_group=geometry_group)

    @staticmethod
    def _map_params_to_dynamo_inputs(params):
        """Return a dictionary with the input note name as keys with the subsequent parameter values"""

        return {
            "Number of houses": params.step_2.number_of_houses,
            "Number of floors": params.step_2.number_of_floors,
            "Depth": params.step_2.depth,
            "Width": params.step_2.width,
            "Height floor": params.step_2.height_floor,
            "Height roof": params.step_2.height_roof,
        }

    @MapView('Map view', duration_guess=1)  # in seconds, if it is larger or equal to 3, the "update" button will appear
    def get_map_view(self, params: Munch, **kwargs) -> MapResult:
        features = []

        if params.step_1.point:
            center_point = params.step_1.point
            center_x, center_y = center_point.rd[0], center_point.rd[1]
            angle        = params.step_1.angle*pi/180
            height       = params.step_1.depth
            width        = params.step_1.width     
            n_houses = params.step_1.number_of_houses 

            center_x_wgs, center_y_wgs = RDWGSConverter.from_rd_to_wgs((center_x, center_y))
            features.append(MapPoint(center_x_wgs, center_y_wgs))

            coords = []
            for house_index in range(0,n_houses,1):

                #Bottom left corner:
                if house_index==0: #Only computed for the case of 1 house
                    Bot_Left_x = center_x - ((width / 2) * cos(angle)) + ((height / 2) * sin(angle))
                    Bot_Left_y = center_y - ((width / 2) * sin(angle)) - ((height / 2) * cos(angle))
                    coords.append((Bot_Left_x,Bot_Left_y))

                #Top left corner:
                if house_index ==0: #Only computed for the case of 1 house
                    Top_Left_x = center_x - ((width / 2) * cos(angle)) - ((height / 2) * sin(angle))
                    Top_Left_y = center_y - ((width / 2) * sin(angle)) + ((height / 2) * cos(angle))
                    coords.append((Top_Left_x,Top_Left_y))
                
                #Top right corner:
                Top_Right_x = center_x + ((width*(2*house_index+1) / 2) * cos(angle)) - ((height / 2) * sin(angle))
                Top_Right_y = center_y + ((width*(2*house_index+1) / 2) * sin(angle)) + ((height / 2) * cos(angle))
                coords.append((Top_Right_x,Top_Right_y))

                #Bottom right corner:
                Bot_Right_x = center_x + ((width*(2*house_index+1) / 2) * cos(angle)) + ((height / 2) * sin(angle))
                Bot_Right_y = center_y + ((width*(2*house_index+1) / 2) * sin(angle)) - ((height / 2) * cos(angle))
                coords.append((Bot_Right_x,Bot_Right_y))

                map_point_list = []
                for coord in coords:
                    coord_x_converted, coord_y_converted = RDWGSConverter.from_rd_to_wgs(coord)					
                    map_point_list.append(MapPoint(coord_x_converted, coord_y_converted))

                polygon_coords = []
                if house_index ==0: #Regular order for case of 1 house
                    polygon_coords.append(map_point_list[-1])
                    polygon_coords.append(map_point_list[-2])
                    polygon_coords.append(map_point_list[-3])
                    polygon_coords.append(map_point_list[-4])
                
                    features.append(MapPolygon(polygon_coords))

                if house_index>0: #Irregular order for case of more than 1 house
                    polygon_coords.append(map_point_list[-1])
                    polygon_coords.append(map_point_list[-3])
                    polygon_coords.append(map_point_list[-4])
                    polygon_coords.append(map_point_list[-2])
                
                    features.append(MapPolygon(polygon_coords))

        return MapResult(features)


    def download_file(self, params, **kwargs):
        data_output, geometry_group = self.run_dynamo(params)
        print(data_output)

        template_path = Path(__file__).parent.parent/"lib"/"files"/"sample_document.docx"
        components = []
        components.append(WordFileTag('n_houses', params.step_2.number_of_houses))
        components.append(WordFileTag('width', params.step_2.width))
        components.append(WordFileTag('depth', params.step_2.depth))
        components.append(WordFileTag('n_floors', params.step_2.number_of_floors))
        components.append(WordFileTag('height_floor', params.step_2.height_floor))
        components.append(WordFileTag('height_roof', params.step_2.height_roof))

        for key, output in data_output.items():
            components.append(WordFileTag(key, output))



        with open(template_path, 'rb') as template:
            word_file = render_word_file(template, components)

        return DownloadResult(word_file, 'my_word_file.docx')

        # return DownloadResult('this comes in file', 'filename.docx')



                # #Bottom left corner:
                # if house==0: #Only computed for the case of 1 house
                # 	Bot_Left_x = center_x
                # 	Bot_Left_y = center_y
                # 	coords.append((Bot_Left_x,Bot_Left_y))

                # #Top left corner:
                # if house ==0: #Only computed for the case of 1 house
                # 	Top_Left_x = center_x + ((height) * sin(angle))
                # 	Top_Left_y = center_y - ((width) * sin(angle)) + ((height) * cos(angle))
                # 	coords.append((Top_Left_x,Top_Left_y))
                
                # #Top right corner:
                # Top_Right_x = center_x - ((width) * cos(angle)) - ((height) * sin(angle))
                # Top_Right_y = center_y - ((width) * sin(angle)) + ((height) * cos(angle))
                # coords.append((Top_Right_x,Top_Right_y))

                # #Bottom right corner:
                # Bot_Right_x = center_x - ((width) * cos(angle)) + ((height) * sin(angle))
                # Bot_Right_y = center_y - ((width) * sin(angle))
                # coords.append((Bot_Right_x,Bot_Right_y))

        # if params.tab1.section2.line:
        # 	marker = params.tab1.section2.line
        # 	coords_residential = []
        # 	coords = []
        # 	for point in marker.points:
        # 		coords_residential = []
        # 		for property, value in vars(point).items():
        # 			# print(value)
        # 			coords_residential.append(value)
        # 		coords.append(point.rd[0])
        # 		coords.append(point.rd[1])


        # 		# print(point[0])
        # 		moved_y = point.rd[0]+6
        # 		moved_x = point.rd[1]+6
        # 		moved_y_wgs, moved_x_wgs = RDWGSConverter.from_rd_to_wgs((moved_y, moved_x))
        # 		# features.append(MapPoint(moved_y_wgs, moved_x_wgs))
        # 		features.append(MapPoint(coords_residential[0], coords_residential[1]))
        # 		# features.append(MapPoint(GeoPoint((point[0],point[1]))))
        # 		# features.append(MapPoint(GeoPoint.from_rd((moved_y,moved_x))))

        # 		# moved_x_y = (moved_y,moved_x)
        # 		coords_residential.append(GeoPoint.from_rd((moved_y,moved_x)))
        # 		lat, lon = RDWGSConverter.from_rd_to_wgs((100000, 400000))
        # 		# coords_residential.append(moved_x_y)
        # 		# print(point.rd[1])
        # 		# point_tuple = {point}
        # 		# print(point_tuple)

        # 	# Phi = 90
        # 	# h=6
        # 	w=3
        # 	cx = point.rd[0]
        # 	cy = point.rd[1]

        # 	h = sqrt( (coords[2] - coords[0])**2 + (coords[3] - coords[1])**2 )
        # 	Phi = abs((coords[3]-coords[1])/(coords[2]-coords[0]))


        # 	x = cx + w * cos(Phi) - h * sin(Phi)
        # 	y = cy + w * sin(Phi) + h * cos(Phi)


        # 	transformed_x_wgs, transformed_y_wgs = RDWGSConverter.from_rd_to_wgs((x, y))
        # 	# features.append(MapPoint(transformed_x_wgs, transformed_y_wgs))

        # 	# print(cx, "transformerd to: ", x)
        # 	# print(cy, "transformerd to: ", y)
        # 	# center(1,1) = (center_x,center_y)

        

        # print(coords_residential)
            
            # features.append(MapPoint(coords_residential))
            # features.append(MapPolyline.from_geo_polyline(marker))
            # features.append(MapPolygon(coords_residential))

        # if params.tab1.section2.polygon:
        # 	marker = params.tab1.section2.polygon
        # 	features.append(MapPolygon.from_geo_polygon(marker))

