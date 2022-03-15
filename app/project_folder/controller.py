from viktor.core import ViktorController
from viktor.views import Summary


class ProjectFolderController(ViktorController):

	summary = Summary()
	label = "ProjectFolder"
	children = ["Project"]
	show_children_as = "Table"
	viktor_convert_entity_field = True
