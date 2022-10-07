# GHEtool: An open-source tool for borefield sizing in Python
[![PyPI version](https://badge.fury.io/py/GHEtool.svg)](https://badge.fury.io/py/GHEtool)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.04406/status.svg)](https://doi.org/10.21105/joss.04406)

## What is *GHEtool*?
<img src="https://raw.githubusercontent.com/wouterpeere/GHEtool/main/GHEtool/gui/Icon.png" width="110" align="left">

GHEtool is a Python package that contains all the functionalities needed to deal with borefield design. It is developed for both researchers and practitioners.
The core of this package is the automated sizing of borefield under different conditions. The sizing of a borefield is typically slow due to the high complexity of the mathematical background. Because this tool has a lot of precalculated data (cf. infra), GHEtool can size a borefield in the order of tenths of milliseconds. This sizing typically takes the order of minutes. Therefore, this tool is suited for being implemented in workflows where iterations are required.

#### Graphical user interface
GHEtool also comes with a *graphical user interface (GUI)*. This GUI is prebuilt as an exe-file (only for Windows platforms currently) because this provides access to all the functionalities without coding. A setup to install the GUI at the user-defined place is also implemented and available [here](https://www.mech.kuleuven.be/en/tme/research/thermal_systems/tools/ghetool).
This graphical interface is made by Tobias Blanke from FH Aachen.

<p align="center">
<img src="https://raw.githubusercontent.com/wouterpeere/GHEtool/main/GHEtool/gui/GHEtool.PNG" width="600"></br>
  Screenshot of the GUI.
</p>

## Requirements
This code is tested with Python 3.8 and requires the following libraries (the versions mentioned are the ones with which the code is tested)

* Numpy (>=1.20.2)
* Scipy (>=1.6.2)
* Matplotlib (>=3.4.1)
* Pygfunction (>=2.1.0)
* Openpyxl (>=3.0.7)
* Pandas (>=1.2.4)

For the GUI

* PyQt5 (>=5.10)

For the tests

* Pytest (>=7.1.2)

When working with Python 3.9 and higher, installing a newer version of pygfunction (>=2.1.0) can lead to problems due to the fact that its dependency CoolProp is not compatible with Python 3.9 and higher (see also <https://github.com/CoolProp/CoolProp/issues/1992> and <https://github.com/CoolProp/CoolProp/issues/2119>). If one wants to work with the newer version of pygfunction and with Python 3.9 or higher, one can install a development version of CoolProp using

```
pip install -i https://test.pypi.org/simple/ CoolProp==6.4.2.dev0
```

## Quick start
### Installation

One can install GHEtool by running Pip and running the command

```
pip install GHEtool
```

or one can install a newer development version using

```
pip install --extra-index-url https://test.pypi.org/simple/ GHEtool
```

Developers can clone this repository.

It is a good practise to use virtual environments (venv) when working on a (new) Python project so different Python and package versions don't conflict with eachother. For GHEtool, Python 3.8 is recommended. General information about Python virtual environments can be found [here](https://docs.Python.org/3.9/library/venv.html) and in [this article](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

### Check installation

To check whether everything is installed correctly, run the following command

```
pytest --pyargs GHEtool
```

This runs some predefined cases to see whether all the internal dependencies work correctly. 9 test should pass successfully.

### Get started with GHEtool

To get started with GHEtool, one needs to create a Borefield object. This is done in the following steps.

```Python
from GHEtool import Borefield, GroundData
```

After importing the necessary classes, one sets all the relevant ground data.

```Python
data = GroundData(110, # depth of the field (m)
                  6,   # distance between the boreholes (m)
                  3,   # ground thermal conductivity (W/mK)
                  10,  # initial/undisturbed ground temperature (deg C)
                  0.2, # borehole equivalent resistance (mK/W)
                  10,  # number of boreholes in width direction of the field (/)
                  12,  # number of boreholes in the length direction of the field (/)
                  2.4*10**6) # volumetric heat capacity of the ground (J/m3K) 
```

Furthermore, one needs to set the peak and monthly baseload for both heating and cooling.

```Python
peak_cooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]   # Peak cooling in kW
peak_heating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

monthly_load_heating = [46500.0, 44400.0, 37500.0, 29700.0, 19200.0, 0.0, 0.0, 0.0, 18300.0, 26100.0, 35100.0, 43200.0]        # in kWh
monthly_load_cooling = [4000.0, 8000.0, 8000.0, 8000.0, 12000.0, 16000.0, 32000.0, 32000.0, 16000.0, 12000.0, 8000.0, 4000.0]  # in kWh
```

Next, one creates the borefield object and sets the temperature constraints and the ground data.

```Python
# create the borefield object
borefield = Borefield(simulation_period=20,
                      peak_heating=peak_heating,
                      peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating,
                      baseload_cooling=monthly_load_cooling)

borefield.set_ground_parameters(data)

# set temperature boundaries
borefield.set_max_ground_temperature(16)  # maximum temperature
borefield.set_min_ground_temperature(0)  # minimum temperature
```

Once a Borefield object is created, one can make use of all the functionalities of GHEtool. One can for example size the borefield using:

```Python
depth = borefield.size(100)
print("The borehole depth is: ", depth, "m")
```

Or one can plot the temperature profile by using

```Python
borefield.print_temperature_profile(legend=True)
```

A full list of functionalities is given below.

## Functionalities
GHEtool offers functionalities of value to all different disciplines working with borefields. The features are available both in the code environment and in the GUI. These functions are listed in the table below, alongside with a link to an example document where one can find how these functionalities can be used.

| Functionality | Example document |
| --- | --- |
| Sizing the borefield (i.e. calculating the required depth) for a given injection and extraction load for the borefield (three sizing methods are available). | [main_functionalities.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/main_functionalities.py) |
| Calculating the temperature evolution of the ground for a given building load and borefield configuration | [main_functionalities.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/main_functionalities.py) |
| Using dynamically calculated borehole thermal resistance (this is directly based on the code of pygfunction) | [sizing_with_Rb_calculation.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Validation/sizing_with_Rb_calculation.py) |
| Optimising the load profile for a given heating and cooling load | [optimise_load_profile.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/optimise_load_profile.py)|
| Finding the optimal rectangular borefield configuration for a given heating and cooling load | [size_borefield_by_length_and_width.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/size_borefield_by_length_and_width.py) |
| Importing heating and cooling loads from .csv and .xlsx files | [import_data.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/import_data.py) |
| Using your custom borefield configuration | [custom_borefield_configuration.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/custom_borefield_configuration.py) |

| Comparisons | Example document |
| --- | --- |
| Comparison of different sizing methods (L2, L3) for different random profiles| [sizing_method_comparison.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Validation/sizing_method_comparison.py) |
| Comparison in calculation time and accuracy between using the precalculated gfunction data or not | [speed_comparison.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Validation/speed_comparison.py) |
| Comparison of different sizing methods (L2, L3 and L4) for the same hourly profile | [sizing_method_comparison_L2_L3_L4.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Examples/sizing_method_comparison_L2_L3_L4.py) |
| Comparison in calculation time and accuracy between the simplified L2 sizing methodology and the more accurate L3 method. | [sizing_method_comparison.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Validation/sizing_method_comparison.py) |
| Comparison of Rb* calculation between GHEtool and EED. | [validation_effective_borehole_thermal_resistance.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/Validation/validation_effective_borehole_thermal_resistance.py) |


## Precalculated data
This tool comes with precalculated g-functions for all borefields of type nxm (for 0<n,m<21) for which the boreholes are connected in parallel. For these borefield configurations, the g-functions are calculated for different depth-thermal diffusivity-spacing combinations. The ranges are:

* Depth: 25 - 350m in increments of 25m
* Thermal diffusivity of the soil (defined as thermal conductivity / volumetric heat capacity): 0.036 - 0.144m²/day in increments of 0.018m²/day
(This is equal to a range of thermal conductivity from 1-4W/mK with a constant volumetric heat capacity of 2.4MJ/m³K)
* Spacings (equal): 3 - 9m in increments of 1m

Here a burial depth (D) of 4.0m is assumed even as a borehole radius of 7.5cm for all the precalculated data.

It is possible to calculate your own dataset to your specific project based on the [pygfunction](https://github.com/MassimoCimmino/pygfunction) tool and use this one in the code.

## License

*GHEtool* is licensed under the terms of the 3-clause BSD-license.
See [GHEtool license](LICENSE).

## Contributing to *GHEtool*

You can report bugs and propose enhancements on the
[issue tracker](https://github.com/wouterpeere/GHEtool/issues).
If you want to add new features and contribute to the code,
please contact Wouter Peere (wouter.peere@kuleuven.be).

## Main contributors
Wouter Peere, KU Leuven & boydens engineering (part of Sweco), wouter.peere@kuleuven.be

Tobias Blanke, Solar-Institute Jülich, FH Aachen, blanke@sij.fh-aachen.de

## Citation
Please cite GHEtool using the JOSS paper.

Peere, W., Blanke, T.(2022). _GHEtool: An open-source tool for borefield sizing in Python._ Journal of Open Source Software, 7(76), 4406, https://doi.org/10.21105/joss.04406

## References
### Development of GHEtool
Peere, W., Blanke, T. (2022). _GHEtool: An open-source tool for borefield sizing in Python._ Journal of Open Source Software, 7(76), 4406, https://doi.org/10.21105/joss.04406

Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) _Validated combined first and last year borefield sizing methodology._ In _Proceedings of International Building Simulation Conference 2021_. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180

Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering,
KU Leuven, Belgium.

### Applications/Mentions of GHEtool
M. Sharifi. (2022) Early-Stage Integrated Design Methods for Hybrid GEOTABS Buildings. PhD thesis, Department of Architecture and Urban Planning, Faculty of Engineering and Architecture, Ghent University.

Coninx M., De Nies J. (2022) Cost-efficient Cooling of Buildings by means of Borefields with Active and Passive Cooling. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Michiels E. (2022) Dimensionering van meerdere gekoppelde boorvelden op basis van het type vraagprofiel en de verbinding met de gebruikers. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Vanpoucke B. (2022) Optimale dimensionering van boorvelden door een variabel massadebiet. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Haesen R., Hermans L. (2021) Design and Assessment of Low-carbon Residential District Concepts with (Collective) Seasonal Thermal Energy Storage. Master thesis, Departement of Mechanical Engineering, KU Leuven, Belgium.
