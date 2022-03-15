from viktor.parametrization import Parametrization, Tab, Section, IntegerField, NumberField, Step, TextField

class ExampleParametrization(Parametrization):
    step_1 = Step('Step 1 - without views', next_label="Go to step 2")
    step_1.input_1 = TextField('This is a text field')
    step_1.input_2 = NumberField('This is a number field')

    step_2 = Step('Step 2 - with views', views=['geometry_view', 'data_view'], previous_label="Go to step 1")
    step_2.input_1 = TextField('This is a text field')
    step_2.input_2 = NumberField('This is a number field')

class ResidentialBlockParametrization(Parametrization):

	tab1 = Tab("Tab 1")

	tab1.section1 = Section("Section 1")
	tab1.section1.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=1.0)
	tab1.section1.number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
	tab1.section1.depth = NumberField("Depth", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
	tab1.section1.width = NumberField("Width", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
	tab1.section1.height_floor = NumberField("Height floor", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)
	tab1.section1.height_roof = NumberField("Height roof", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)
