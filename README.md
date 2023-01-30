# GHEtool: An open-source tool for borefield sizing

[![PyPI version](https://badge.fury.io/py/GHEtool.svg)](https://badge.fury.io/py/GHEtool)
[![Tests](https://github.com/wouterpeere/GHEtool/actions/workflows/test.yml/badge.svg)](https://github.com/wouterpeere/GHEtool/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/wouterpeere/GHEtool/branch/main/graph/badge.svg?token=I9WWHW60OD)](https://codecov.io/gh/wouterpeere/GHEtool)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.04406/status.svg)](https://doi.org/10.21105/joss.04406)
[![Downloads](https://static.pepy.tech/personalized-badge/ghetool?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/ghetool)
[![Downloads](https://static.pepy.tech/personalized-badge/ghetool?period=week&units=international_system&left_color=black&right_color=orange&left_text=Downloads%20last%20week)](https://pepy.tech/project/ghetool)
[![Read the Docs](https://readthedocs.org/projects/ghetool/badge/?version=stable)](https://ghetool.readthedocs.io/en/stable/)
## What is *GHEtool*?
<img src="https://raw.githubusercontent.com/wouterpeere/GHEtool/main/docs/sources/gui/_figure/Icon.png" width="110" align="left">

GHEtool is a Python package that contains all the functionalities needed to deal with borefield design. It is developed for both researchers and practitioners.
The core of this package is the automated sizing of borefield under different conditions. By making use of combination of just-in-time calculations of thermal ground responses (using [pygfunction](https://github.com/MassimoCimmino/pygfunction)) with
intelligent interpolation, this automated sizing can be done in the order of milliseconds. Please visit our website [https://GHEtool.eu](https://GHEtool.eu) for more information.

#### Read The Docs
GHEtool has an elaborate documentation were all the functionalities of the tool are explained, with examples, literature and validation.
This can be found on [GHEtool.readthedocs.io](https://ghetool.readthedocs.io).

#### Graphical user interface
GHEtool also comes with a *graphical user interface (GUI)*. This GUI is prebuilt as an exe-file (only for Windows platforms currently) because this provides access to all the functionalities without coding. A setup to install the GUI at the user-defined place is also implemented and available at [https://GHEtool.eu](https://GHEtool.eu).

<p align="center">
<img src="https://raw.githubusercontent.com/wouterpeere/GHEtool/main/docs/sources/gui/_figure/GHEtool.PNG" width="600">
</p>

## Requirements
This code is tested with Python 3.8, 3.9, 3.10 and 3.11 and requires the following libraries (the versions mentioned are the ones with which the code is tested)

* Numpy (>=1.20.2)
* Scipy (>=1.6.2)
* Matplotlib (>=3.4.1)
* Pygfunction (>=2.2.1)
* Openpyxl (>=3.0.7)
* Pandas (>=1.2.4)

For the GUI

* PySide6 (>=6.4.1)
* configparser (>=5.3.0)

For the tests

* Pytest (>=7.1.2)

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

It is a good practise to use virtual environments (venv) when working on a (new) Python project so different Python and package versions don't conflict with eachother. For GHEtool, Python 3.8 or higher is recommended. General information about Python virtual environments can be found [here](https://docs.Python.org/3.9/library/venv.html) and in [this article](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

### Check installation

To check whether everything is installed correctly, run the following command

```
pytest --pyargs GHEtool
```

This runs some predefined cases to see whether all the internal dependencies work correctly. All test should pass successfully.

### Get started with GHEtool

To get started with GHEtool, one needs to create a Borefield object. This is done in the following steps.

```Python
from GHEtool import Borefield, GroundData
```

After importing the necessary classes, one sets all the relevant ground data and borehole equivalent resistance.

```Python
data = GroundData(3,   # ground thermal conductivity (W/mK)
                  10,  # initial/undisturbed ground temperature (deg C)
                  0.2, # borehole equivalent resistance (mK/W)
                  2.4*10**6) # volumetric heat capacity of the ground (J/m3K) 
```

Furthermore, one needs to set the peak and monthly baseload for both heating and cooling.

```Python
peak_cooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]   # Peak cooling in kW
peak_heating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

monthly_load_heating = [46500.0, 44400.0, 37500.0, 29700.0, 19200.0, 0.0, 0.0, 0.0, 18300.0, 26100.0, 35100.0, 43200.0]        # in kWh
monthly_load_cooling = [4000.0, 8000.0, 8000.0, 8000.0, 12000.0, 16000.0, 32000.0, 32000.0, 16000.0, 12000.0, 8000.0, 4000.0]  # in kWh
```

Next, one creates the borefield object in GHEtool and sets the temperature constraints and the ground data.

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

```Python
# set a rectangular borefield
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
```

Note that the borefield can also be set using the pygfunction package.

```Python
import pygfunction as gt

# set a rectangular borefield
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075) 
borefield.set_borefield(borefield_gt)
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
GHEtool offers functionalities of value to all different disciplines working with borefields. The features are available both in the code environment and in the GUI.
For more information about the functionalities of GHEtool, please visit the [ReadTheDocs](https://ghetool.readthedocs.org).

## License

*GHEtool* is licensed under the terms of the 3-clause BSD-license.
See [GHEtool license](LICENSE).

## Contact GHEtool
- Do you want to contribute to GHEtool?
- Do you have a great idea for a new feature?
- Do you have a specific remark/problem?

Please do contact us at [wouter@ghetool.eu](mailto:wouter@ghetool.eu).

## Citation
Please cite GHEtool using the JOSS paper.

Peere, W., Blanke, T.(2022). GHEtool: An open-source tool for borefield sizing in Python. _Journal of Open Source Software, 7_(76), 4406, https://doi.org/10.21105/joss.04406

For more information on how to cite GHEtool, please visit the ReadTheDocs at [GHEtool.readthedocs.io](https://ghetool.readthedocs.io/en/stable/).


## References

### Development of GHEtool
Peere, W., Blanke, T. (2022). GHEtool: An open-source tool for borefield sizing in Python. _Journal of Open Source Software, 7_(76), 4406, https://doi.org/10.21105/joss.04406

Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021). Validated combined first and last year borefield sizing methodology. In _Proceedings of International Building Simulation Conference 2021_. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180

Peere, W. (2020). Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering,
KU Leuven, Belgium.

### Applications/Mentions of GHEtool

Cimmino, M., Cook., J. C. (2022). pygfunction 2.2 : New Features and Improvements in Accuracy and Computational Efficiency. In _Proceedings of IGSHPA Research Track 2022_. Las Vegas (USA), 6-8 December 2022. https://doi.org/10.22488/okstate.22.000015

Verleyen, L., Peere, W., Michiels, E., Boydens, W., Helsen, L. (2022). The beauty of reason and insight: a story about 30 years old borefield equations. _IEA HPT Magazine 40_(3), 36-39, https://doi.org/10.23697/6q4n-3223

Peere, W., Boydens, W., Helsen, L. (2022). GHEtool: een open-sourcetool voor boorvelddimensionering. Presented at the 15e warmtepompsymposium: van uitdaging naar aanpak, Quadrivium, Heverlee, België.

Peere, W., Coninx, M., De Nies, J., Hermans, L., Boydens, W., Helsen, L. (2022). Cost-efficient Cooling of Buildings by means of Borefields with Active and Passive Cooling. Presented at the 15e warmtepompsymposium: van uitdaging naar aanpak, Quadrivium, Heverlee, België.

Peere, W. (2022). Technologieën voor de energietransitie. Presented at the Energietransitie in meergezinswoningen en kantoorgebouwen: uitdagingen!, VUB Brussel Bruxelles - U Residence.

Sharifi., M. (2022). Early-Stage Integrated Design Methods for Hybrid GEOTABS Buildings. PhD thesis, Department of Architecture and Urban Planning, Faculty of Engineering and Architecture, Ghent University.

Coninx, M., De Nies, J. (2022). Cost-efficient Cooling of Buildings by means of Borefields with Active and Passive Cooling. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Michiels, E. (2022). Dimensionering van meerdere gekoppelde boorvelden op basis van het type vraagprofiel en de verbinding met de gebruikers. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Vanpoucke, B. (2022). Optimale dimensionering van boorvelden door een variabel massadebiet. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Haesen R., Hermans L. (2021). Design and Assessment of Low-carbon Residential District Concepts with (Collective) Seasonal Thermal Energy Storage. Master thesis, Departement of Mechanical Engineering, KU Leuven, Belgium.
