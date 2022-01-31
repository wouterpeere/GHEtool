# GHEtool: A open-source tool for borefield sizing in Python


## What is *GHEtool*?
*GHEtool* is a Python module for both the sizing of geothermal borefields and for plotting the temperature profile of the ground for a given load. Currently, the code is in full development and this version includes the core functions, so developers, researchers and practitioners can use it in their workflow. A graphical interface is being developed at this stage.
At its core, *GHEtool* is based on the ground thermal response functions (g-functions in short). These were precalculated for rectangular fields up to 20x20 boreholes with the python package *pygfunction* (Cimmino, 2018) so the code can interpolate from these data. Because of a lot of iterations, such precalculated database is useful. One can also add its own configurations.
Using temporal superposition of the load, *GHEtool* calculates the required depth of the borefield in order to stay between the given temperature limits. It can, on the other hand, also calculate the temperature profile for a given depth. 

It is also possible to use a fixed borefield and an hourly load profile to calculate the maximum peak (based on a load-duration curve) that can be put on the field.

This tool is based on the work of (Peere et al., 2021).

## Graphical user interface
In the GUI folder, one can find a graphical interface which makes it easy to interact with the code environment. The graphical tool is also available as a stand-alone *.exe with and without the command interface.
This graphical interface is made by Tobias Blanke from RWTH Aachen. 

## Precalculated data
This tool comes with precalculated g-functions for all borefields of type nxm (for 0<n,m<20) for which the boreholes are connected in parallel. For these borefield configurations, the g-functions are calculated for different depth-thermal conductivity-spacing combinations. The ranges are:

* Depth: 25 - 350m in increments of 25m
* Thermal conductivity of the soil: 1 - 4 in increments of 0.5W/mk
* Spacings (equal): 3 - 9m in increments of 1m

Here a burial depth (D) of 4.0m is assumed even as a borehole radius of 7.5cm.

It is possible to calculate your own dataset to your specific project based on the *pygfunction* tool and use this one in the code.

## Requirements
This code is tested with Python 3.9 and requires the following libraries (the versions mentioned are the ones with which the code is tested)

* Numpy (>=1.20.2)
* Scipy (>=1.6.2)
* Matplotlib (>=3.4.1)
* Pygfunction (>=1.1.2)
* Tkinter (>=0.1.0)
* Openpyxl (>=3.0.7)
* Pandas (>=1.2.4)

## Main contributors
Wouter Peere, KU Leuven & Boydens Engineering (part of Sweco), wouter.peere@kuleuven.be
Tobias Blanke, FH Aachen, blanke@sij.fh-aachen.de

## References
Cimmino, M. (2018). _pygfunction: an open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields_. In _Proceedings of eSim 2018, the 10th conference of IBPSA- Canada_. Montréal, QC, Canada, May 9-10.

Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. _Validated combined first and last year borefield sizing methodology._ In _Proceedings of International Building Simulation Conference 2021_ (2021). Brugge (Belgium), 1-3 September 2021.
