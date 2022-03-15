from viktor.parametrization import Parametrization, Tab, Section, IntegerField, NumberField, GeoPointField, GeoPolylineField, GeoPolygonField

class ResidentialBlockParametrization(Parametrization):

	tab1 = Tab("Tab 1")

	tab1.section1 = Section("Section 1")
	tab1.section1.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=1.0)
	tab1.section1.number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
	tab1.section1.depth = NumberField("Depth", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
	tab1.section1.width = NumberField("Width", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
	tab1.section1.height_floor = NumberField("Height floor", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)
	tab1.section1.height_roof = NumberField("Height roof", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)

class ExampleParametrisation(Parametrization):
	"""Defines the input fields in left-side of the web UI in the GeoAnalysis entity (Editor)."""
	location = Tab("Location")
	location.point = GeoPointField("enter a point")
	location.line = GeoPolylineField("draw a line")
	location.polygon = GeoPolygonField("draw a closed shape")