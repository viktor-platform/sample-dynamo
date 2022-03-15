from viktor.parametrization import Parametrization, Tab, Section, NumberField, GeoPointField

class ResidentialBlockParametrization(Parametrization):

	tab1 = Tab("Model parameters")

	tab1.section1 = Section("Input building")
	tab1.section1.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=1.0)
	tab1.section1.number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
	tab1.section1.depth = NumberField("Depth", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
	tab1.section1.width = NumberField("Width", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
	tab1.section1.height_floor = NumberField("Height floor", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)
	tab1.section1.height_roof = NumberField("Height roof", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)

	tab1.section2 = Section("Input map")
	tab1.section2.point = GeoPointField("Draw a point")
	tab1.section2.angle = NumberField("Angle (degrees)", min=0.0, max=360.0, variant='slider', step=1.0, default=0)

	

