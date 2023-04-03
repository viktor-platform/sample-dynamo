# Tuturial dynamo 

## Introduction 

In this tutorial, we will learn how to seamlessly integrate a dynamo model into the Viktor platform. With the help of Dynamo Sandbox, a visual programming tool for creating complex parametric models, we can efficiently produce accurate 3D models. 

To start, the user provides the necessary parameters for the dynamo model within the Viktor application. The Viktor worker then computes the dynamo model using the command-line interface included within Dynamo Sandbox. The geometry of the model is generated using either Autodesk Revit or FormIt. The geometry JSON is then converted to a mesh, which is rendered and visualized in Viktor.

In addition to creating the app, this tutorial will also cover common troubleshooting issues that may arise during the integration process. Furthermore, we will discuss how to install the worker, which is required to run the analysis.

## Setting up worker 
A worker is a program that connects VIKTOR with third-party software to execute tasks and retrieve results through the platform.  The worker communicates with the VIKTOR cloud via an encrypted  connection, eliminating the need to open public ports on the network. For Dynamo integration, the generic worker must be installed. Follow the steps below:

1. Select the generic worker. The installer starts an installation wizard from which the worker can be configured. Administrator rights on the machine are required to perform the installation.

2. Specification of the installation directory. The standard directory that is used for the installation is: C:\Program Files\Viktor\Viktor for 

```
C:\Program Files\Viktor\Viktor for <application> <software package> <version>
```
3. Configuration of the worker. Using the installation wizard you will be asked to fill the required information step-by-step. During this installation wizard you are asked for your  credentials 

4. For the credentials follow the steps that are shown in the picture below:

![My Image](Images_readme/Credentials.png)
$\qquad$ 4.1 Go to workers tab 

$\qquad$ 4.2 Press the button "Create worker" (top right)

$\qquad$ 4.3 Fill in the description, allocation to specific and use your workspace  

$\qquad$ 4.4 Press on create, you will get the following pop up(see figure below). Paste the credential code and placed in it in the install wizard immediately. Viktor will not preserve this data for security reasons.


![My Image](Images_readme/Credentials_popup.png)

5. Next step is to install formit [Download link](https://formit.autodesk.com/)

6. Open the **config.yaml** inside the same folder as the generic worker executive(see step 2)

Delete everything inside the file. The config file should contain the path to the DynamoSandbox executable, that is automatically installed with Formit

Additionally, the file should contain the following arguments:

- Dynamo script, -o (open)
- Geometry file, -v (output)
- Path to local installation of Autodesk FormIt or Revit, -gp (geometry path)
- Json file, -g (geometry file)

The temporary dynamo script, geometry file and json file are created within the worker folder.

An example of the code for the file named  **config.yaml** is shown below:

```
<pre><code>executables:
  dynamo:
    path: 'C:\Program Files\Autodesk\FormIt\DynamoSandbox\DynamoWPFCLI.exe'
    arguments:
    - '-o'
    - 'input.dyn'
    - '-v'
    - 'output.xml'
    - '-gp'
    - 'C:\Program Files\Autodesk\FormIt' 
    - '-g'
    - 'geometry.json'
maxParallelProcesses: 1 # must be one, please do not change
</code></pre>
```

For more information about the Dynamo CLI is referred to: https://github.com/DynamoDS/Dynamo/wiki/Dynamo-Command-Line-Interface

7. Run the **viktor-worker-gneric** file as an administrator. You should see a green bullet in the top right corner, see red circle in figure below. This means the worker succesfoll installed.

![My Image](Images_readme/Connection.png)

## Updating model 
The dynamo file has got the following input paramaters:
| Parameter  | User input |
| ------------- | ------------- |
| Number of houses | {{n_houses}}  |
| Width  | {{width}}  |
| Depth | {{depth}}  |
| Number of floors  | {{n_floors}}  |
| Height floor  | {{height_floor}}  |
| Height roof  | {{height_roof}}  |


### Paramatrization zone 
The next is to add inputfields in the paramatrization to fill in the variables of the dynamo file. We will use the numberfield. See code below:
```
from viktor.parametrization import ViktorParametrization, NumberField

class Parametrization(ViktorParametrization):

    # Input fields
    number_of_houses = NumberField("Number of houses", max=8.0, min=1.0, variant='slider', step=1.0, default=3.0)
    number_of_floors = NumberField("Number of floors", max=5.0, min=1.0, variant='slider', step=1.0, default=2.0)
    depth = NumberField("Depth [m]", max=10.0, min=5.0, variant='slider', step=1.0, default=8.0)
    width = NumberField("Width [m]", max=6.0, min=4.0, variant='slider', step=1.0, default=5.0)
    height_floor = NumberField("Height floor", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5, suffix='m')
    height_roof = NumberField("Height roof", max=3.0, min=2.0, variant='slider', step=0.1, default=2.5, suffix='m')
    
```

### Updating model 
