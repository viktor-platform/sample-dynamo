from viktor.core import ViktorController
from viktor.views import Summary


class ProjectController(ViktorController):

	summary = Summary()
	label = "Project"
	children = ["ResidentialBlock"]
	show_children_as = "Table"
	viktor_convert_entity_field = True
