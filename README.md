# GHEtool: An open-source tool for borefield sizing

[![PyPI version](https://badge.fury.io/py/GHEtool.svg)](https://badge.fury.io/py/GHEtool)
[![Conda version](https://anaconda.org/conda-forge/ghetool/badges/version.svg)](https://anaconda.org/conda-forge/ghetool)
[![Tests](https://github.com/wouterpeere/GHEtool/actions/workflows/test.yml/badge.svg)](https://github.com/wouterpeere/GHEtool/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/wouterpeere/GHEtool/branch/main/graph/badge.svg?token=I9WWHW60OD)](https://codecov.io/gh/wouterpeere/GHEtool)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.04406/status.svg)](https://doi.org/10.21105/joss.04406)
[![Downloads](https://static.pepy.tech/personalized-badge/ghetool?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/ghetool)
[![Downloads](https://static.pepy.tech/personalized-badge/ghetool?period=week&units=international_system&left_color=black&right_color=orange&left_text=Downloads%20last%20week)](https://pepy.tech/project/ghetool)
[![Read the Docs](https://readthedocs.org/projects/ghetool/badge/?version=latest)](https://ghetool.readthedocs.io/en/latest/)

## What is *GHEtool*?

<img src="https://raw.githubusercontent.com/wouterpeere/GHEtool/main/docs/Icon.png" width="110" align="left">

GHEtool is a Python package that contains all the functionalities needed to deal with borefield design. GHEtool has been
developed as a joint effort of KU Leuven (The SySi Team), boydens engineering (part of Sweco) and FH Aachen and is
currently being maintained by Enead BV.
The core of this package is the automated sizing of borefield under different conditions. By making use of combination
of just-in-time calculations of thermal ground responses (
using [pygfunction](https://github.com/MassimoCimmino/pygfunction)) with
intelligent interpolation, this automated sizing can be done in the order of milliseconds. Please visit our
website [https://GHEtool.eu](https://GHEtool.eu) for more information.

### Read The Docs

GHEtool has an elaborate documentation where all the functionalities of the tool are explained, with examples,
literature
and validation. This can be found
on [https://ghetool.readthedocs.io/en/latest/](https://ghetool.readthedocs.io/en/latest/).

## Graphical user interface

There are two graphical user interfaces available which are built using GHEtool: GHEtool Cloud and GHEtool Community

#### GHEtool Cloud

GHEtool Cloud is the official and supported version of GHEtool which supports drilling companies, engineering firms,
architects, government organizations in their geothermal design process.
With GHEtool Cloud they can minimize the environmental and societal impact while maximizing the cost-effective
utilization of geothermal projects.
Visit our website at [https://ghetool.eu](https://ghetool.eu) to learn more about GHEtool Cloud and what it can do for
you.

<p align="center">
<img src="https://ghetool.eu/wp-content/uploads/2024/08/GHEtool-Cloud-squarish.png" width="600">
</p>

#### GHEtool Community

Besides GHEtool Cloud, an open-source alternative for the graphical user interface is available in the form of *GHEtool
Community*.
This version is built and maintained by the community, and **has no official support like GHEtool Cloud**. You can read
all about this
*GHEtool Community* on their [GitHub repo](https://github.com/wouterpeere/ghetool-gui).

### Development

GHEtool is in constant development with new methods, enhancements and features added to every new version. Please visit
our [project board](https://github.com/users/wouterpeere/projects/2) to check our progress.

## Requirements

This code is tested with Python 3.9, 3.10, 3.11, 3.12 and 3.13 and requires the following libraries (the versions
mentioned are the ones with which the code is tested)

* matplotlib >= 3.9.2
* numpy >= 1.26.4
* pandas >= 1.4.3
* pygfunction >= 2.3.0
* scipy >= 1.8.1
* secondarycoolantprops >= 1.1

For the tests

* pytest >= 7.1.2

For the active/passive example

* optuna >= 3.6.1

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

GHEtool is also available as a conda package. Therefore, you can install GHEtool with the command:

````
conda install GHEtool
````

Developers can clone this repository.

It is a good practise to use virtual environments (venv) when working on a (new) Python project so different Python and
package versions don't conflict with eachother. For GHEtool, Python 3.8 or higher is recommended. General information
about Python virtual environments can be found [here](https://docs.Python.org/3.9/library/venv.html) and
in [this article](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

### Check installation

To check whether everything is installed correctly, run the following command

```
pytest --pyargs GHEtool
```

This runs some predefined cases to see whether all the internal dependencies work correctly. All test should pass
successfully.

## Get started with GHEtool

### Building blocks of GHEtool

GHEtool is a flexible package that can be extend with methods
from [pygfunction](https://pygfunction.readthedocs.io/en/stable/).
To work efficiently with GHEtool, it is important to understand the main structure of the package.

#### Borefield

The Borefield object is the central object within GHEtool. It is within this object that all the calculations and
optimizations take place.
All attributes (ground properties, load data ...) are set inside the borefield object.

#### Ground properties

Within GHEtool, there are multiple ways of setting the ground data. Currently, your options are:

* _GroundConstantTemperature_: if you want to model your borefield with a constant, known ground temperature.
* _GroundFluxTemperature_: if you want to model your ground with a varying ground temperature due to a constant
  geothermal heat flux.
* _GroundTemperatureGradient_: if you want to model your ground with a varying ground temperature due to a geothermal
  gradient.

* You can also use multiple ground layers to define your ground model. Please take a look
  at [our example](https://ghetool.readthedocs.io/en/latest/sources/code/Examples/start_in_different_month.html).

Please note that it is possible to add your own ground types by inheriting the attributes from the abstract _GroundData
class.

#### Pipe data

Within GHEtool, you can use different structures for the borehole internals: U-tubes or coaxial pipes.
Concretely, the classes you can use are:

* _Multiple U-tubes_
* _Single U-tubes (special case of multiple U-tubes)_
* _Double U-tubes (special case of multiple U-tubes)_
* _Coaxial pipe_
* _Conical pipe_ (like the GEROtherm VARIO and FLUX probes from
  HakaGerodur ([learn more]('https://www.hakagerodur.ch/de/gerotherm-vario/')))
* _Separatus tube_: The Separatus geothermal heat exchanger is an innovation in the geothermal domain. It consists of a
  single, DN50 pipe with a unique 'splitpipe'-technology that separates the cold and the hot side of the fluid. For
  design purposes, it is advised to use this with rather small borehole diameters of DN90. For more information, visit
  the [separatus website](https://separatus.ch/en/). An example in GHEtool can be
  found [here](https://ghetool.readthedocs.io/en/latest/sources/code/Examples/separatus.html).
* _Turbocollector_: The Turbocollector from Muovitech has internal fins which enhances the turbulent flow character
  at lower flow rates. Visit their website for more
  information [turbocollector website](https://www.muovitech.com/group/?page=turbo). An example in GHEtool can be
  found [here](https://ghetool.readthedocs.io/en/latest/sources/code/Examples/turbocollector.html).

Please note that it is possible to add your own pipe types by inheriting the attributes from the abstract _PipeData
class.

#### Fluid data

You can set the fluid data by using the FluidData class.

* _ConstantFluidData_: Temperature independent fluid properties
* _TemperatureDependentFluidData_: Temperature dependent fluid data (Water, MPG, MEG, MMA, MEA, Thermox DTX, Coolflow
  NTP)

#### Flow rate data

Currently, only constant flow rates are compatible with GHEtool, but this will change in the future.

* _ConstantFlowRate_

#### Efficiency data

Within GHEtool, you can work with both seasonal efficiencies (SCOP and SEER) and temperature dependent efficiencies (COP
and SEER).
These efficiencies can be used in the Building load classes (cf. infra). The different available efficiency classes are:

* _SCOP_: Constant seasonal performance for heating
* _SEER_: Constant seasonal performance for cooling
* _COP_: Instant efficiency for heating, with inlet temperature, outlet temperature and part load dependency
* _EER_: Instant efficiency for cooling, with inlet temperature, outlet temperature and part load dependency
* _EERCombined_: EER for combined active and passive cooling

#### Load data

One last element which you will need in your calculations, is the load data. Within GHEtool, there are three important
aspects
when it comes to choosing the right load data class.

1. _Load type_: Do you want to work with building (i.e. secondary) or geothermal (i.e. primary) load?
2. _Resolution type_: Do you want to work with monthly or hourly data?
3. _Multiyear_: Do you want to assume a building/geothermal demand that is constant over the simulation period or do you
   want to enter the load for multiple years?

Depending on your answer on these three questions, you can opt for one of eight different load classes:

* _MonthlyGeothermalLoadAbsolute_: You can set the monthly baseload and peak load for extraction and injection for
  one standard year which will be used for all years within the simulation period.
* _HourlyGeothermalLoad_: You can set (or load) the hourly extraction and injection load of a standard year which will
  be used for all years within the simulation period.
* _HourlyGeothermalLoadMultiYear_: You can set (or load) the hourly extraction and injection load for multiple years (
  i.e. for the whole simulation period).
* _MonthlyGeothermalLoadMultiYear_: You can set the monthly extraction and injection load for multiple years (i.e. for
  the whole simulation period).
* _MonthlyBuildingLoadAbsolute_: You can set the monthly baseload and peak load for heating and cooling for
  one standard year which will be used for all years within the simulation period.
* _HourlyBuildingLoad_: You can set (or load) the hourly heating and cooling load of a standard year which will
  be used for all years within the simulation period.
* _HourlyBuildingLoadMultiYear_: You can set (or load) the hourly heating and cooling load for multiple years (
  i.e. for the whole simulation period).
* _MonthlyBuildingLoadMultiYear_: You can set the monthly heating and cooling load for multiple years (i.e. for
  the whole simulation period).

On the other hand, you can also choose a Cluster load where you can add multiple loads together. Be careful however when
mixing hourly and monthly loads!

All building load classes also have the option to add a yearly domestic hot water (DHW) demand and require you to define
an
efficiency for heating, cooling (and optionally DHW) (cf. supra).

Please note that it is possible to add your own load types by inheriting the attributes from the abstract _LoadData,
_HourlyLoad, _LoadDataBuilding and _HourlyLoadBuilding classes.

### Options for sizing methods

Like always with iterative methods, there is a trade-off between speed and accuracy. Within GHEtool (using the
CalculationSetup class) one can alter different parameters
to customize the behaviour they want. Note that these options are additive, meaning that, for example, the strongest
criteria from the
atol and rtol is chosen when sizing. The options are:

* _atol_: For the sizing methods, an absolute tolerance in meters between two consecutive iterations can be set.
* _rtol_: For the sizing methods, a relative tolerance in meters between two consecutive iterations can be set.
* _max_nb_of_iterations_: For the sizing methods, a maximum number of iterations can be set. If the size is not
  converged, a RuntimeError is thrown.
* _use_precalculated_dataset_: This option makes sure the custom g-function dataset (if available) is not used.
* _interpolate_gfunctions_: Calculating the gvalues gives a large overhead cost, although they are not that sensitive to
  a change in borehole length. If this parameter is True
  it is allowed that gfunctions are interpolated. (To change the threshold for this interpolation, go to the Gfunction
  class.)
* _deep_sizing_: An alternative sizing method for cases with high injection (peaks) and a variable ground temperature.
  This method is potentially slower, but proves to be more robust.
* _force_deep_sizing_: When the alternative method from above should always be used.

### Simple example

To show how all the pieces of GHEtool work together, below you can find a step-by-step example of how, traditionally,
one would work with GHEtool.
Start by importing all the relevant classes. In this case we are going to work with a ground model which assumes a
constant ground temperature (e.g. from a TRT-test),
and we will provide the load with a monthly resolution.

```Python
from GHEtool import Borefield, GroundConstantTemperature, MonthlyGeothermalLoadAbsolute
```

After importing the necessary classes, the relevant ground data parameters are set.

```Python
data = GroundConstantTemperature(3,  # ground thermal conductivity (W/mK)
                                 10,  # initial/undisturbed ground temperature (deg C)
                                 2.4 * 10 ** 6)  # volumetric heat capacity of the ground (J/m3K) 
```

Furthermore, for our loads, we need to set the peak loads as well as the monthly base loads for extraction and
injection.

```Python
peak_injection = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak injection in kW
peak_extraction = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak extract in kW

monthly_load_extraction = [46500.0, 44400.0, 37500.0, 29700.0, 19200.0, 0.0, 0.0, 0.0, 18300.0, 26100.0, 35100.0,
                           43200.0]  # in kWh
monthly_load_injection = [4000.0, 8000.0, 8000.0, 8000.0, 12000.0, 16000.0, 32000.0, 32000.0, 16000.0, 12000.0, 8000.0,
                          4000.0]  # in kWh

# set load object
load = MonthlyGeothermalLoadAbsolute(monthly_load_extraction, monthly_load_injection, peak_extraction, peak_injection)

```

Next, we create the borefield object in GHEtool and set the temperature constraints and the ground data.
Here, since we do not use a pipe and fluid model (
see [Examples](https://ghetool.readthedocs.io/en/stable/sources/code/examples.html) if you need examples where no
borehole thermal resistance is given),
we set the borehole equivalent thermal resistance.

```Python
# create the borefield object
borefield = Borefield(load=load)

# set ground parameters
borefield.set_ground_parameters(data)

# set the borehole equivalent resistance
borefield.Rb = 0.12

# set temperature boundaries
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
```

Next we create a rectangular borefield.

```Python
# set a rectangular borefield
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
```

Note that the borefield can also be set using the [pygfunction](https://pygfunction.readthedocs.io/en/stable/) package,
if you want more complex designs.

```Python
import pygfunction as gt

# set a rectangular borefield
borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
borefield.set_borefield(borefield_gt)
```

Once a Borefield object is created, one can make use of all the functionalities of GHEtool. One can for example size the
borefield using:

```Python
length = borefield.size()
print("The borehole length is: ", length, "m")
```

Or one can plot the temperature profile by using

```Python
borefield.print_temperature_profile(legend=True)
```

A full list of functionalities is given below.

## Functionalities

GHEtool offers functionalities of value to all different disciplines working with borefields. The features are available
both in the code environment and in the GUI.
For more information about the functionalities of GHEtool, please visit the documentation
on [https://ghetool.readthedocs.io/en/latest/](https://ghetool.readthedocs.io/en/latest/).

## License

*GHEtool* is licensed under the terms of the 3-clause BSD-license (see [GHEtool license](LICENSE)).
For professional licenses, contact us at [info@ghetool.eu](mailto:info@ghetool.eu).

## Contact GHEtool

- Do you want to support GHEtool financially or by contributing to our software?
- Do you have a great idea for a new feature?
- Do you have a specific remark/problem?

Please do contact us at [info@ghetool.eu](mailto:info@ghetool.eu).

## Citation

Please cite GHEtool using the JOSS paper.

Peere, W., Blanke, T.(2022). GHEtool: An open-source tool for borefield sizing in Python. _Journal of Open Source
Software, 7_(76), 4406, https://doi.org/10.21105/joss.04406

For more information on how to cite GHEtool, please visit the ReadTheDocs
at [https://ghetool.readthedocs.io/en/latest/](https://ghetool.readthedocs.io/en/latest/).

## References

### Development of GHEtool

Meertens, L., Peere, W., Helsen, L. (2024). Influence of short-term dynamic effects on geothermal borefield size. In
_Proceedings of International Ground Source Heat Pump Association_. Montréal (Canada), 28-30 May 2024.

Coninx, M., De Nies, J., Hermans, L., Peere, W., Boydens, W., Helsen, L. (2024). Cost-efficient cooling of buildings by
means of geothermal borefields with active and passive cooling. _Applied Energy_, 355, Art. No.
122261, https://doi.org/10.1016/j.apenergy.2023.122261.

Peere, W., Hermans, L., Boydens, W., and Helsen, L. (2023). Evaluation of the oversizing and computational speed of
different open-source borefield sizing methods. In _Proceedings of International Building Simulation Conference 2023_.
Shanghai (Belgium), 4-6 September 2023.

Coninx, M., De Nies, J. (2022). Cost-efficient Cooling of Buildings by means of Borefields with Active and Passive
Cooling. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Peere, W., Blanke, T. (2022). GHEtool: An open-source tool for borefield sizing in Python. _Journal of Open Source
Software, 7_(76), 4406, https://doi.org/10.21105/joss.04406

Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021). Validated combined first and last year
borefield sizing methodology. In _Proceedings of International Building Simulation Conference 2021_. Brugge (Belgium),
1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180

Peere, W. (2020). Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis,
Department of Mechanical Engineering,
KU Leuven, Belgium.

### Applications/Mentions of GHEtool

Aitmad, M. (2025). Techno-Economic Analysis of using Ground-Source Heat Exchangers in Pakistan (Master thesis).

Jahn, A. (2024). Softwarekonzept zur vereinfachten Wärmeplanung von Städten und Quartieren bei variabler Datenbasis (
Master thesis).

Meertens, L. (2024). Reducing Capital Cost for Geothermal Heat Pump Systems Through Dynamic Borefield Sizing. _IEA HPT
Magazine 42_(2), https://doi.org/10.23697/9r3w-jm57.

Blanke, T., Born, H., Döring, B. et al. Model for dimensioning borehole heat exchanger applied to
mixed-integer-linear-problem (MILP) energy system optimization. _Geotherm Energy_ 12, 30 (
2024). https://doi.org/10.1186/s40517-024-00301-w.

Dion G., Pasquier, P., Perraudin, D. (2024). Sizing equation based on the outlet fluid temperature of closed-loop ground
heat exchangers. In _Proceedings of International Ground Source Heat Pump Association_. Montréal (Canada), 28-30 May

2024.

Peere, W. (2024). Are Rules of Thumb Misleading? The Complexity of Borefield Sizing and the Importance of Design
Software. _IEA HPT Magazine 42_(1), https://doi.org/10.23697/7nec-0g78.

Meertens, L. (2024). Invloed van dynamische korte-termijneffecten op de dimensionering van geothermische boorvelden.
Master thesis, Department of Mechanical Engineering, KU Lueven, Belgium.

Weynjes, J. (2023). Methode voor het dimensioneren van een geothermisch systeem met regeneratie binnen verschillende
ESCO-structuren. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Hermans, L., Haesen, R., Uytterhoeven, A., Peere, W., Boydens, W., Helsen, L. (2023). Pre-design of collective
residential solar districts with seasonal thermal energy storage: Importance of level of detail. _Applied thermal
engineering_ 226, Art.No. 120203, 10.1016/j.applthermaleng.2023.120203

Cimmino, M., Cook., J. C. (2022). pygfunction 2.2 : New Features and Improvements in Accuracy and Computational
Efficiency. In _Proceedings of IGSHPA Research Track 2022_. Las Vegas (USA), 6-8 December

2022. https://doi.org/10.22488/okstate.22.000015.

Verleyen, L., Peere, W., Michiels, E., Boydens, W., Helsen, L. (2022). The beauty of reason and insight: a story about
30 years old borefield equations. _IEA HPT Magazine 40_(3), 36-39, https://doi.org/10.23697/6q4n-3223.

Peere, W., Boydens, W., Helsen, L. (2022). GHEtool: een open-sourcetool voor boorvelddimensionering. Presented at the
15e warmtepompsymposium: van uitdaging naar aanpak, Quadrivium, Heverlee, België.

Peere, W., Coninx, M., De Nies, J., Hermans, L., Boydens, W., Helsen, L. (2022). Cost-efficient Cooling of Buildings by
means of Borefields with Active and Passive Cooling. Presented at the 15e warmtepompsymposium: van uitdaging naar
aanpak, Quadrivium, Heverlee, België.

Peere, W. (2022). Technologieën voor de energietransitie. Presented at the Energietransitie in meergezinswoningen en
kantoorgebouwen: uitdagingen!, VUB Brussel Bruxelles - U Residence.

Sharifi., M. (2022). Early-Stage Integrated Design Methods for Hybrid GEOTABS Buildings. PhD thesis, Department of
Architecture and Urban Planning, Faculty of Engineering and Architecture, Ghent University.

Coninx, M., De Nies, J. (2022). Cost-efficient Cooling of Buildings by means of Borefields with Active and Passive
Cooling. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Michiels, E. (2022). Dimensionering van meerdere gekoppelde boorvelden op basis van het type vraagprofiel en de
verbinding met de gebruikers. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

Vanpoucke, B. (2022). Optimale dimensionering van boorvelden door een variabel massadebiet. Master thesis, Department of
Mechanical Engineering, KU Leuven, Belgium.

Haesen R., Hermans L. (2021). Design and Assessment of Low-carbon Residential District Concepts with (Collective)
Seasonal Thermal Energy Storage. Master thesis, Departement of Mechanical Engineering, KU Leuven, Belgium.
