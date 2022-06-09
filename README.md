# GHEtool: An open-source tool for borefield sizing in Python
[![PyPI version](https://badge.fury.io/py/GHEtool.svg)](https://badge.fury.io/py/GHEtool)
[![status](https://joss.theoj.org/papers/0ae2224874ee0139d6f28baa48fe9127/status.svg)](https://joss.theoj.org/papers/0ae2224874ee0139d6f28baa48fe9127)

## What is *GHEtool*?
<img src="https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/Icon.png" width="110" align="left">

GHEtool is a python package that contains all the functionalities needed to deal with borefield design. It is developed for both researchers and practitioners.
The core of this package is the automated sizing of borefield under different conditions. The sizing of a borefield is typically slow due to the high complexity of the mathematical background. Because this tool has a lot of precalculated data (cf. infra), GHEtool can size a borefield in the order of tenths of milliseconds. This sizing typically takes the order of minutes. Therefore, this tool is suited for being implemented in workflows where iterations are required.

#### Graphical user interface
GHEtool also comes with a *graphical user interface (GUI)*. This GUI is prebuilt as an exe-file because this provides access to all the functionalities without coding. A setup to install the GUI at the user-defined place is also implemented and available [here](https://www.mech.kuleuven.be/en/tme/research/thermal_systems/tools/ghetool).
This graphical interface is made by Tobias Blanke from FH Aachen.

<p align="center">
<img src="https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/GHEtool.PNG" width="600"></br>
  Screenshot of the GUI.
</p>


## Functionalities
GHEtool offers functionalities of value to all different disciplines working with borefields. The features are available both in the code environment and in the GUI. These features are:
* Sizing the borefield (i.e. calculating the required depth) for a given injection and extraction load for the borefield (two sizing methods are available). The tool can work with monthly and hourly load profiles
* Finding the optimal rectangular borefield configuration for a given heating and cooling load
* Optimising the load profile for a given heating and cooling load
* Using dynamically calculated borehole thermal resistance (this is directly based on the code of pygfunction)
* Calculating the temperature evolution of the ground for a given building load and borefield configuration
* Importing heating and cooling loads from *.csv and *.xlsx files
* Using your custom borefield configuration

In the example and validation folder, one can find information on how to use this functionalities.

## Precalculated data
This tool comes with precalculated g-functions for all borefields of type nxm (for 0<n,m<21) for which the boreholes are connected in parallel. For these borefield configurations, the g-functions are calculated for different depth-thermal conductivity-spacing combinations. The ranges are:

* Depth: 25 - 350m in increments of 25m
* Thermal conductivity of the soil: 1 - 4 in increments of 0.5W/mk
* Spacings (equal): 3 - 9m in increments of 1m

Here a burial depth (D) of 4.0m is assumed even as a borehole radius of 7.5cm for all the precalculated data.

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

For the GUI

* PyQt5 (>=5.10)

## Quick start

One can install GHEtool by running Pip and running the command

```
pip install GHEtool
```

Developers can clone this repository.

It is a good practise to use virtual environments (venv) when working on a (new) python project so different python and package versions don't conflict with eachother. For GHEtool, python 3.9 is recommended. General information about python virtual environments can be found [here](https://docs.python.org/3.9/library/venv.html) and in [this article](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

## License

*GHEtool* is licensed under the terms of the 3-clause BSD-license.
See [GHEtool license](LICENSE).

## Contributing to *GHEtool*

You can report bugs and propose enhancements on the
[issue tracker](https://github.com/wouterpeere/GHEtool/issues).
If you want to add new features and contribute to the code,
please contact Wouter Peere (wouter.peere@kuleuven.be).

## Main contributors
Wouter Peere, KU Leuven & Boydens Engineering (part of Sweco), wouter.peere@kuleuven.be

Tobias Blanke, Solar-Institute Jülich, FH Aachen, blanke@sij.fh-aachen.de


## References
Cimmino, M. (2018). _pygfunction: an open-source toolbox for the evaluation of thermal response factors for geothermal borehole fields_. In _Proceedings of eSim 2018, the 10th conference of IBPSA- Canada_. Montréal, QC, Canada, May 9-10.

Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. _Validated combined first and last year borefield sizing methodology._ In _Proceedings of International Building Simulation Conference 2021_ (2021). Brugge (Belgium), 1-3 September 2021.
