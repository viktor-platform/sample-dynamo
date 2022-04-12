from viktor.parametrization import Parametrization, NumberField, GeoPointField, Step, DownloadButton, Text


class ResidentialBlockParametrization(Parametrization):

    step_1 = Step('Map', views="get_map_view", next_label="Go to step 2")
    
    step_1.text1 = Text("""Location definition
    \n Choose the desired location for the residential block on the map.""")
    step_1.point = GeoPointField("Draw a point")

    step_1.text2 = Text("""Maximum needed space
    \n Choose the parameters defining the maximum needed space for the residential block. Set the rotation.""")    
    step_1.angle = NumberField("Rotation (degrees)", min=0.0, max=360.0, variant='slider', step=1.0, default=0)
    step_1.depth = NumberField("Depth [m]", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
    step_1.width = NumberField("Width [m]", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)	
    step_1.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=3.0)

    step_2 = Step("3D model", views="geometry_and_data_view", next_label="Go to step 3")
    step_2.text1 = Text("""Parameters definition
    \n Choose the parameters for the dynamo visualization of the residential block. 
    Then, press the update button to create the visualization. This could take a few seconds. 
    The dynamo model is created and converted to the format used for visualization within Viktor. 
    Each time the parameters are updated, press the update button to refresh the results. 
    The model can be turned around by pressing and holding the left mouse button on the model.""")
    step_2.number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=3.0)
    step_2.number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
    step_2.depth = NumberField("Depth [m]", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
    step_2.width = NumberField("Width [m]", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
    step_2.height_floor = NumberField("Height floor [m]", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)
    step_2.height_roof = NumberField("Height roof [m]", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5)

    step_2.text2 = Text("""Numerical output
    \n On the right-hand side the numerical output on the residential block is generated, based on the dynamo model. The output is related to the selected parameters.""")


    step_3 = Step("Report", views="get_pdf_view")
    step_3.text1 = Text("""Create a report of the output results of the dynamo model. This includes the floor area per house, total project cost, MKI and CO2 emission.
    Also the selected parameters are included. A sample of the report is shown on the right side of the screen.""")
    step_3.download_btn = DownloadButton('Download report (docx)','download_file')
