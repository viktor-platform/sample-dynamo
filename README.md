![](https://img.shields.io/badge/SDK-v13.0.0-blue) <Please check version is the same as specified in requirements.txt>

# Sample application dynamo integration Viktor

In this sample application a solution is presented how to integrate a dynamo model within the Viktor platform. 
The user provides the parameters for the dynamo model within the Viktor application. 
With these parameters, the dynamo model is computed by the Viktor worker. This is done with the command line interface included within DynamoSandbox. 
The geometry is created with the help of either Autodesk Revit or FormIt. The geometry JSON is then converted to mesh, which is rendered and visualized in Viktor. 

An example of the application is shown in the image below.

![Alt text](README_image.jpg?raw=true "Example")

## Setting up worker
A worker is necessary in order to run this application. Below is described how to configure the worker:

1. Install the generic worker
2. Install DynamoSandbox (http://dynamobim.org/download/)
3. Install either Autodesk Revit or FormIt
**Note:** *Autodesk Formit can be installed without accepting any terms and conditions / end-user license agreements. 
After starting the program you are asked to sign in to your autodesk account, 
however, you can use the geometry DLLs with DynamoSandbox without doing this.*

4. Create a new file named **config.yaml** inside same folder as the worker executive. 

The config file should contain the path to the DynamoSandbox executable.

Additionally, the file should contain the following arguments:

- Dynamo script, -o (open)
- Geometry file, -v (output)
- Path to local installation of Autodesk FormIt or Revit, -gp (geometry path)
- Json file, -g (geometry file)

The temporary dynamo script, geometry file and json file are created within the worker folder.

An example of the code for the file named  **config.yaml** is shown below:

<pre><code>executables:
  dynamo:
    path: "C:\Users\Administrator\Documents\$USERNAME$\DynamoSandbox\DynamoWPFCLI.exe"
    arguments:
    - '-o'
    - 'input.dyn'
    - '-v'
    - 'output.xml'
    - '-gp'
    - 'C:\Program Files\Autodesk\FormIt'  # or Revit
    - '-g'
    - 'geometry.json'
maxParallelProcesses: 1 # must be one, please do not change
</code></pre>

For more information about the Dynamo CLI is referred to: https://github.com/DynamoDS/Dynamo/wiki/Dynamo-Command-Line-Interface

## Setting up dynamo model
A few settings are required within the dynamo model in order for Viktor to recognize the input and output. Simply put the
parameters you want to adjust in the Viktor application to "Is Input" by right-mouse clicking on the node. Same goes for the output
parameters, then select "Is Output". The name of the node should be the same as the name called by the Dynamo module in your script.




