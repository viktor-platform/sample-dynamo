from viktor.views import MapPoint, MapPolygon
from viktor.geometry import RDWGSConverter

from math import cos, sin, pi


def house_on_map(params, features):
    center_point = params.step_1.point
    center_x, center_y = center_point.rd[0], center_point.rd[1]
    angle = params.step_1.angle * pi / 180
    height = params.step_1.depth
    width = params.step_1.width
    n_houses = params.step_1.number_of_houses

    center_x_wgs, center_y_wgs = RDWGSConverter.from_rd_to_wgs((center_x, center_y))
    features.append(MapPoint(center_x_wgs, center_y_wgs))

    coords = []  # Coordinates of the outer corners of the residential block are computed and stored in a list.
    for house_index in range(0, n_houses, 1):

        # Bottom left corner:
        if house_index == 0:  # Only computed for the case of 1 house
            Bot_Left_x = center_x - ((width / 2) * cos(angle)) + ((height / 2) * sin(angle))
            Bot_Left_y = center_y - ((width / 2) * sin(angle)) - ((height / 2) * cos(angle))
            coords.append((Bot_Left_x, Bot_Left_y))

        # Top left corner:
        if house_index == 0:  # Only computed for the case of 1 house
            Top_Left_x = center_x - ((width / 2) * cos(angle)) - ((height / 2) * sin(angle))
            Top_Left_y = center_y - ((width / 2) * sin(angle)) + ((height / 2) * cos(angle))
            coords.append((Top_Left_x, Top_Left_y))

        # Top right corner:
        Top_Right_x = center_x + ((width * (2 * house_index + 1) / 2) * cos(angle)) - (
                (height / 2) * sin(angle))
        Top_Right_y = center_y + ((width * (2 * house_index + 1) / 2) * sin(angle)) + (
                (height / 2) * cos(angle))
        coords.append((Top_Right_x, Top_Right_y))

        # Bottom right corner:
        Bot_Right_x = center_x + ((width * (2 * house_index + 1) / 2) * cos(angle)) + (
                (height / 2) * sin(angle))
        Bot_Right_y = center_y + ((width * (2 * house_index + 1) / 2) * sin(angle)) - (
                (height / 2) * cos(angle))
        coords.append((Bot_Right_x, Bot_Right_y))

        map_point_list = []
        for coord in coords:
            coord_x_converted, coord_y_converted = RDWGSConverter.from_rd_to_wgs(coord)
            map_point_list.append(MapPoint(coord_x_converted, coord_y_converted))

        polygon_coords = []
        if house_index == 0:  # Regular order drawing a polygon for case of 1 house
            polygon_coords.append(map_point_list[-1])
            polygon_coords.append(map_point_list[-2])
            polygon_coords.append(map_point_list[-3])
            polygon_coords.append(map_point_list[-4])

            features.append(MapPolygon(polygon_coords))

        if house_index > 0:  # Irregular order drawing a polygon for case of more than 1 house
            polygon_coords.append(map_point_list[-1])
            polygon_coords.append(map_point_list[-3])
            polygon_coords.append(map_point_list[-4])
            polygon_coords.append(map_point_list[-2])

            features.append(MapPolygon(polygon_coords))

            return features
