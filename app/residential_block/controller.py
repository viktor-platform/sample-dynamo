from viktor.core import ViktorController
from viktor.views import Summary, DataGroup, GeometryAndDataView, GeometryAndDataResult, PDFView, PDFResult
from viktor.views import MapView, MapResult
from viktor.utils import convert_word_to_pdf
from viktor import UserException
from munch import Munch

from pathlib import Path
from viktor.result import DownloadResult
from viktor.external.word import WordFileTag, render_word_file
from .house_on_map import house_on_map

from .parametrization import ResidentialBlockParametrization
from .run_dynamo import run_dynamo


class ResidentialBlockController(ViktorController):
    parametrization = ResidentialBlockParametrization
    summary = Summary()
    label = "ResidentialBlock"
    children = []
    show_children_as = None

    @GeometryAndDataView("Building 3D", duration_guess=5)
    def geometry_and_data_view(self, params, **kwargs):

        # Run the dynamo module and retrieve output geometry and data
        glb_file, dataview_output_items, dynamo_output_report = run_dynamo(params)

        # Some exceptions are raised to direct the user of the application in a certain direction.
        if params.step_2.number_of_houses > params.step_1.number_of_houses:
            raise UserException(
                "Number of houses is larger than provided in step 1! Please go back to step 1 and increase the number of houses.")

        if params.step_2.width > params.step_1.width:
            raise UserException(
                "The width is larger than provided in step 1! Please go back to step 1 and increase the width.")

        if params.step_2.depth > params.step_1.depth:
            raise UserException(
                "The depth is larger than provided in step 1! Please go back to step 1 and increase the depth.")

        return GeometryAndDataResult(geometry=glb_file, data=DataGroup(*dataview_output_items))

    @PDFView('PDF view', duration_guess=3)
    def get_pdf_view(self, params, **kwargs):
        word_doc = self.render_word_report(params)

        with word_doc.open_binary() as word_file:
            pdf_file = convert_word_to_pdf(word_file)
        return PDFResult(file=pdf_file)

    @MapView('Map view', duration_guess=1)  # in seconds, if it is larger or equal to 3, the "update" button will appear
    def get_map_view(self, params: Munch, **kwargs) -> MapResult:
        # Create empty list to store the features for the mapview
        features = []

        # Whenever a point is created on the map, rectangles are drawn onto the map with the input parameters
        if params.step_1.point:
            features = house_on_map(params, features)

        return MapResult(features)

    def download_file(self, params, **kwargs):
        word_file = self.render_word_report(params)

        return DownloadResult(word_file, 'my_word_file.docx')

    @staticmethod
    def render_word_report(params):
        """This method creates a word file report based on the user input parameters and the numerical output from
        the dynamo model"""
        glb_file, dataview_output_items, dynamo_output_report = run_dynamo(params)

        template_path = Path(__file__).parent.parent / "lib" / "files" / "sample_document.docx"
        components = [WordFileTag('n_houses', params.step_2.number_of_houses),
                      WordFileTag('width', params.step_2.width), WordFileTag('depth', params.step_2.depth),
                      WordFileTag('n_floors', params.step_2.number_of_floors),
                      WordFileTag('height_floor', params.step_2.height_floor),
                      WordFileTag('height_roof', params.step_2.height_roof),
                      WordFileTag('floor_area', dynamo_output_report['result_floor_area'][0]),
                      WordFileTag('total_cost', dynamo_output_report['result_total_cost'][0]),
                      WordFileTag('MKI', dynamo_output_report['result_MKI'][0]),
                      WordFileTag('CO2', dynamo_output_report['result_floor_CO2'][0])]

        with open(template_path, 'rb') as template:
            word_file = render_word_file(template, components)
        return word_file


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
