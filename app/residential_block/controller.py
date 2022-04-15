
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
from .dynamo_utils import run_dynamo, create_dynamo_file, from_decode_to_file, convert_dynamo_file_to_data_items, \
    get_dynamo_output_results, decode_file


class ResidentialBlockController(ViktorController):
    parametrization = ResidentialBlockParametrization
    summary = Summary()
    label = "ResidentialBlock"
    children = []
    show_children_as = None

    @staticmethod
    def run_dynamo_from_params(params):
        """This method runs the dynamo model by using the params as input."""
        # Step 1: create a Dynamo input file
        dynamo_input_file = create_dynamo_file(params)
        # Step 2: Run the dynamo model. As the dynamo run is memoized, the input file needs
        #  to be json serializable. Therefore the conversion first needs to take place.
        serialized_input_file = decode_file(dynamo_input_file.generate())
        decoded_output_files = run_dynamo(serialized_input_file)
        # The output files are returned as decoded strings. These first then need to be converted
        #  back to their preferred formats.
        glb_file = from_decode_to_file(decoded_output_files['glb_file'])
        output_file = from_decode_to_file(decoded_output_files['output_file'])
        return dynamo_input_file, glb_file, output_file

    @GeometryAndDataView("Building 3D", duration_guess=5)
    def geometry_and_data_view(self, params, **kwargs):

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

        # Run the dynamo module and retrieve output geometry and data
        dynamo_input_file, glb_file, output_file = self.run_dynamo_from_params(params)
        dataview_output_items = convert_dynamo_file_to_data_items(dynamo_input_file, output_file)

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
        """This method is triggered when clicking the 'Download report (docx)' button."""
        word_file = self.render_word_report(params)

        return DownloadResult(word_file, 'my_word_file.docx')

    def render_word_report(self, params):
        """This method creates a word file report based on the user input parameters and the numerical output from
        the dynamo model"""

        # Run the dynamo module and retrieve output geometry and data
        dynamo_input_file, glb_file, output_file = self.run_dynamo_from_params(params)
        dynamo_output_results = get_dynamo_output_results(dynamo_input_file, output_file)

        template_path = Path(__file__).parent.parent / "lib" / "files" / "sample_document.docx"
        components = [WordFileTag('n_houses', params.step_2.number_of_houses),
                      WordFileTag('width', params.step_2.width), WordFileTag('depth', params.step_2.depth),
                      WordFileTag('n_floors', params.step_2.number_of_floors),
                      WordFileTag('height_floor', params.step_2.height_floor),
                      WordFileTag('height_roof', params.step_2.height_roof),
                      WordFileTag('floor_area', dynamo_output_results['result_floor_area']['value']),
                      WordFileTag('total_cost', dynamo_output_results['result_total_cost']['value']),
                      WordFileTag('MKI', dynamo_output_results['result_MKI']['value']),
                      WordFileTag('CO2', dynamo_output_results['result_floor_CO2']['value'])]

        with open(template_path, 'rb') as template:
            word_file = render_word_file(template, components)
        return word_file
