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

## Requirements
This code is tested with Python 3.8 and requires the following libraries (the versions mentioned are the ones with which the code is tested)

* Numpy (>=1.20.2)
* Scipy (>=1.6.2)
* Matplotlib (>=3.4.1)
* Pygfunction (>=1.1.2)
* Openpyxl (>=3.0.7)
* Pandas (>=1.2.4)

For the GUI

* PyQt5 (>=5.10)

For the tests

* Pytest (>=7.1.2)

## Quick start
### Installation

One can install GHEtool by running Pip and running the command

```
pip install GHEtool
```

Developers can clone this repository.

It is a good practise to use virtual environments (venv) when working on a (new) python project so different python and package versions don't conflict with eachother. For GHEtool, python 3.9 is recommended. General information about python virtual environments can be found [here](https://docs.python.org/3.9/library/venv.html) and in [this article](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

### Check installation

To check whether everything is installed correctly, run the following command

```
pytest --pyargs GHEtool
```

This runs some predefined cases to see whether all the internal dependencies work correctly. 9 test should pass successfully.

### Get started with GHEtool

To get started with GHEtool, one needs to create a Borefield object. This is done in the following steps.

```python
from GHEtool import Borefield, GroundData
```

After importing the necessary classes, one sets all the relevant ground data.

```python
data = GroundData(110, # depth of the field (m)
                  6,   # distance between the boreholes (m)
                  3,   # ground thermal conductivity (W/mK)
                  10,  # initial/undisturbed ground temperature (deg C)
                  0.2, # borehole equivalent resistance (mK/W)
                  10,  # number of boreholes in width direction of the field (/)
                  12)  # number of boreholes in the length direction of the field (/)
```

Furthermore, one needs to set the peak and monthly baseload for both heating and cooling.

```python
peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]   # Peak cooling in kW
peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

monthlyLoadHeating = [46500.0, 44400.0, 37500.0, 29700.0, 19200.0, 0.0, 0.0, 0.0, 18300.0, 26100.0, 35100.0, 43200.0]        # in kWh
monthlyLoadCooling = [4000.0, 8000.0, 8000.0, 8000.0, 12000.0, 16000.0, 32000.0, 32000.0, 16000.0, 12000.0, 8000.0, 4000.0]  # in kWh
```

Next, one creates the borefield object and sets the temperature constraints and the ground data.

```python
# create the borefield object
borefield = Borefield(simulationPeriod=20,
                      peakHeating=peakHeating,
                      peakCooling=peakCooling,
                      baseloadHeating=monthlyLoadHeating,
                      baseloadCooling=monthlyLoadCooling)

borefield.setGroundParameters(data)

# set temperature boundaries
borefield.setMaxGroundTemperature(16)   # maximum temperature
borefield.setMinGroundTemperature(0)    # minimum temperature
```

Once a Borefield object is created, one can make use of all the functionalities of GHEtool. One can for example size the borefield using:

```python
depth = borefield.size(100)
print("The borehole depth is: ", depth, "m")
```

Or one can plot the temperature profile by using

```python
borefield.printTemperatureProfile(legend=True)
```

A full list of functionalities is given below.

## Functionalities
GHEtool offers functionalities of value to all different disciplines working with borefields. The features are available both in the code environment and in the GUI. These functions are listed in the table below, alongside with a link to an example document where one can find how these functionalities can be used.

| Functionality | Example document |
| --- | --- |
| Sizing the borefield (i.e. calculating the required depth) for a given injection and extraction load for the borefield (two sizing methods are available). | [Main_Functionalities.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/Main_Functionalities.py) |
| Calculating the temperature evolution of the ground for a given building load and borefield configuration | [Main_Functionalities.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/Main_Functionalities.py) |
| Using dynamically calculated borehole thermal resistance (this is directly based on the code of pygfunction) | [Sizing_With_Rb_Calculation.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Validation/Sizing_With_Rb_Calculation.py) |
| Optimising the load profile for a given heating and cooling load | [Optimise_Load_Profile.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/Optimise_Load_Profile.py)|
| Finding the optimal rectangular borefield configuration for a given heating and cooling load | |
| Importing heating and cooling loads from .csv and .xlsx files | [Import_Data.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/Import_Data.py) |
| Using your custom borefield configuration | [Custom_Borefield_Configuration.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/Custom_Borefield_Configuration.py) |

## Precalculated data
This tool comes with precalculated g-functions for all borefields of type nxm (for 0<n,m<21) for which the boreholes are connected in parallel. For these borefield configurations, the g-functions are calculated for different depth-thermal conductivity-spacing combinations. The ranges are:

* Depth: 25 - 350m in increments of 25m
* Thermal conductivity of the soil: 1 - 4 in increments of 0.5W/mk
* Spacings (equal): 3 - 9m in increments of 1m

Here a burial depth (D) of 4.0m is assumed even as a borehole radius of 7.5cm for all the precalculated data.

It is possible to calculate your own dataset to your specific project based on the *pygfunction* tool and use this one in the code.

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
