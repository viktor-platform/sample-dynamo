from viktor.parametrization import Parametrization, Tab, Section, NumberField, GeoPointField, Step, DownloadButton, Text

class ResidentialBlockParametrization(Parametrization):

    step_1 = Step('Map', views="get_map_view", next_label="Go to step 2")
    
    step_1.text1 = Text("""Location definition
    \n Choose the desired location for the residential block on the map""")
    step_1.point = GeoPointField("Draw a point")

    step_1.text2 = Text("""Maximum needed space
    \n Choose the parameters defining the maximum needed space for the residential block. Set the rotation.""")    
    step_1.angle = NumberField("Rotation (degrees)", min=0.0, max=360.0, variant='slider', step=1.0, default=0)
    step_1.depth = NumberField("Depth", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
    step_1.width = NumberField("Width", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)	
    step_1.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=3.0)

    step_2 = Step("3D model", views="geometry_and_data_view", next_label="Go to step 3")

    step_2.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=3.0)
    step_2.number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
    step_2.depth = NumberField("Depth", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
    step_2.width = NumberField("Width", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
    step_2.height_floor = NumberField("Height floor", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)
    step_2.height_roof = NumberField("Height roof", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)

    step_3 = Step("Report")

    step_3.download_btn = DownloadButton('Download','download_file')





	

