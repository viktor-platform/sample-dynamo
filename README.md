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

4. Create a new file with the extension .bat, including the paths that are passed to de dynamo CLI. 
The file should contain the following paths and commands:

- Dynamo Sandbox executable
- Dynamo script, -o (open)
- Geometry file, -v (output)
- Autodesk FormIt or Revit, -gp (geometrypath)
- Json file, -g (geometry file)

An example of the code for the file named **run_dynamo_script.bat** is shown below:

<pre><code>@echo off
"C:\Users\Administrator\Documents\”USERNAME”\DynamoSandbox\DynamoWPFCLI.exe" 
-o "C:\Users\Administrator\Documents\”USERNAME”\dynamo_sample_app\script.dyn" 
-v "C:\Users\Administrator\Documents\”USERNAME”\dynamo_sample_app\output.xml" 
-gp "C:\Program Files\Autodesk\FormIt" 
-g "C:\Users\Administrator\Documents\”USERNAME”\dynamo_sample_app\mesh.json"</code></pre>

For more information about the Dynamo CLI is referred to: https://github.com/DynamoDS/Dynamo/wiki/Dynamo-Command-Line-Interface

5. Create a new file named **config.yaml** inside same folder as the worker executive. The config file should contain the following:
- The .bat file
- The working directory of the worker

An example of the code for the file named  **config.yaml** is shown below:

<pre><code>executables:
  dynamo:
    path: 'C:\Users\Administrator\Documents\”USERNAME”\dynamo_sample_app\run_dynamo_script.bat' 
    workingDirectoryPath: 'C:\Users\Administrator\Documents\”USERNAME”\dynamo_sample_app'
maxParallelProcesses: 1 # must be one, please do not change</code></pre>




