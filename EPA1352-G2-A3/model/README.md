# Simple Transport Model Demo in MESA

Created by: 
Yilin HUANG 

Email:
y.huang@tudelft.nl

Version:
1.1

## Introduction

A simple transport model demo in MESA for EPA1352 Advanced Simulation course Assignment 3. 

## How to Use

* Launch the simulation model with visualization
```
    $ python model_viz.py
```

* Launch the simulation model without visualization
```
    $ python model_run.py
```

## Files

* [model.py](model.py): Contains the model `BangladeshModel` which is a subclass of Mesa `Model`. It reads a `csv` file with specific format for (transport) model generation. (See the README in the `data` directory for data format.) In addition to dynamic behavior, each model component instance (i.e., object) also has geo-location variables, i.e. latitude and longitude in Decimal Degrees (DD). The given bounds of the latitude and longitude of all objects are translated into the bounds of the HTML5 canvas, which is used in case the visualization is launched. 

    In this file, you modify the model generation and add your own routines.

* [components.py](components.py): Contains the model component definitions for the (main) model. Check the file carefully to see which components are already defined. 
  
    In this file, you modify and add your own components.

* [model_viz.py](A3_model_viz.py): Sets up the visualization; uses the `SimpleCanvas` element defined. Calls the model. Run the visualization server.

    In this file, you define simple visualization.

* [model_run.py](model_run.py): Sets up the model run (conditions). Calls the model. Run the simulation without visualization. 

    In this file, you define model batch runs.
  
* [ContinuousSpace](ContinuousSpace): The directory contains files needed to visualize Python3 Mesa models on a continuous canvas with geo-coordinates, a functionality not contained in the current Mesa package. 
  
    Editing files in this directory is NOT recommended for our assignment. 
 
* [ContinuousSpace/SimpleContinuousModule.py](ContinuousSpace/SimpleContinuousModule.py): Defines ``SimpleCanvas``, the Python side of a custom visualization module for drawing objects with continuous positions. This is a slight adaptation of the Flocker example provided by the Mesa project. 
  
    Editing this file is NOT recommended for our assignment. 
  
* [ContinuousSpace/simple_continuous_canvas.js](ContinuousSpace/simple_continuous_canvas.js): JavaScript side of the ``SimpleCanvas`` visualization module. It takes the output generated by the Python ``SimpleCanvas`` element and draws it in the browser window via HTML5 canvas. It can draw circles and rectangles. Both can have text annotation. This file is an adaptation of the Flocker example provided by the Mesa project. 
  
    Editing this file is NOT recommended for our assignment. 
 