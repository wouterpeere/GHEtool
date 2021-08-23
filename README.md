# GHEtool: A open-source tool for borefield sizing in Python


## What is *GHEtool*?
*GHEtool* is a Python module for both the sizing of geothermal borefields and for plotting the temperature profile of the ground for a given load. Currently, the code is in full development and this version includes the core functions, so developers, researchers and practitioners can use it in their workflow. A graphical interface is being developed at this stage.
At its core, *GHEtool* is based on the ground thermal response functions (g-functions in short). These were precalculated for rectangular fields up to 20x20 boreholes with the python package *pygfunction* (Cimmino, 2018) so the code can interpolate from these data. Because of a lot of iterations, such precalculated database is useful. One can also add its own configurations.
Using temporal superposition of the load, *GHEtool* calculates the required depth of the borefield in order to stay between the given temperature limits. It can, on the other hand, also calculate the temperature profile for a given depth. 

This tool is based on the work of (Peere et al., 2021).

## Precalculated data
This tool comes with precalculated g-functions for all borefields of type nxm (for 0<n,m<21). For these borefield configurations, the g-functions are calculated for different depth-thermal conductivity-spacing combinations. The ranges are:

* Depth: 25 - 200m in increments of 25m (will shortly be extended to 300m)
* Thermal conductivity of the soil: 1.5 - 3.5 in increments of 0.5W/mk
* Spacings (equal): 3 - 9m in increments of m-1m

It is possible to calculate your own dataset to your specific project based on the *pygfunction* tool and use this one in the code.

## References
Cimmino, M. (2018). _pygfunction: an open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields_. In _Proceedings of eSim 2018, the 10th conference of IBPSA- Canada_. Montréal, QC, Canada, May 9-10.

Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. _Validated combined first and last year borefield sizing methodology._ In _Proceedings of International Building Simulation Conference 2021_ (2021). Brugge (Belgium), 1-3 September 2021.
