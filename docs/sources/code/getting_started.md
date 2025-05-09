# Installation

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

## Installation

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

This runs some predefined cases to see whether all the internal dependencies work correctly. 9 test should pass
successfully.

# Get started with GHEtool

## Building blocks of GHEtool

GHEtool is a flexible package that can be extend with methods
from [pygfunction](https://pygfunction.readthedocs.io/en/stable/) (
and [ScenarioGUI](https://github.com/tblanke/ScenarioGUI) for the GUI part).
To work efficiently with GHEtool, it is important to understand the main structure of the package.

### Borefield

The Borefield object is the central object within GHEtool. It is within this object that all the calculations and
optimizations take place.
All attributes (ground properties, load data ...) are set inside the borefield object.

### Ground properties

Within GHEtool, there are multiple ways of setting the ground data. Currently, your options are:

* _GroundConstantTemperature_: if you want to model your borefield with a constant, know ground temperature.
* _GroundFluxTemperature_: if you want to model your ground with a varying ground temperature due to a constant
  geothermal heat flux.
* _GroundTemperatureGradient_: if you want to model your ground with a varying ground temperature due to a geothermal
  gradient.

* You can also use multiple ground layers to define your ground model. Please take a look
  at [our example](https://ghetool.readthedocs.io/en/latest/sources/code/Examples/start_in_different_month.html).

Please note that it is possible to add your own ground types by inheriting the attributes from the abstract _GroundData
class.

### Pipe data

Within GHEtool, you can use different structures for the borehole internals: U-tubes or coaxial pipes.
Concretely, the classes you can use are:

* _Multiple U-tubes_
* _Single U-tubes (special case of multiple U-tubes)_
* _Double U-tubes (special case of multiple U-tubes)_
* _Coaxial pipe_
* _Separatus tube_: The Separatus geothermal heat exchanger is an innovation in the geothermal domain. It consists of a
  single, DN50 pipe with a unique 'splitpipe'-technology that separates the cold and the hot side of the fluid. For
  design purposes, it is advised to use this with rather small borehole diameters of DN90. For more information visit
  the [Separatus website]('https://separatus.ch/en/').

Please note that it is possible to add your own pipe types by inheriting the attributes from the abstract _PipeData
class.

#### Fluid data

You can set the fluid data by using the FluidData class.

* _ConstantFluidData_: Temperature independent fluid properties
* _TemperatureDependentFluidData_: Temperature dependent fluid data (Water, MPG, MEG, MMA, MEA)

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

### Load data

One last element which you will need in your calculations, is the load data. Within GHEtool, there are three important
aspects
when it comes to choosing the right load data class.

1. _Load type_: Do you want to work with building (i.e. secondary) or geothermal (i.e. primary) load?
2. _Resolution type_: Do you want to work with monthly or hourly data?
3. _Multiyear_: Do you want to assume a building/geothermal demand that is constant over the simulation period or do you
   want to enter the load for multiple years?

Depending on your answer on these three questions, you can opt for one of eight different load classes:

* _MonthlyGeothermalLoadAbsolute_: You can set one the monthly baseload and peak load for extraction and injection for
  one standard year which will be used for all years within the simulation period.
* _HourlyGeothermalLoad_: You can set (or load) the hourly extraction and injection load of a standard year which will
  be used for all years within the simulation period.
* _HourlyGeothermalLoadMultiYear_: You can set (or load) the hourly extraction and injection load for multiple years (
  i.e. for the whole simulation period).
* _MonthlyGeothermalLoadMultiYear_: You can set the monthly extraction and injection load for multiple years (i.e. for
  the whole simulation period).
* _MonthlyBuildingLoadAbsolute_: You can set one the monthly baseload and peak load for heating and cooling for
  one standard year which will be used for all years within the simulation period.
* _HourlyBuildingLoad_: You can set (or load) the hourly heating and cooling load of a standard year which will
  be used for all years within the simulation period.
* _HourlyBuildingLoadMultiYear_: You can set (or load) the hourly heating and cooling load for multiple years (
  i.e. for the whole simulation period).
* _MonthlyBuildingLoadMultiYear_: You can set the monthly heating and cooling load for multiple years (i.e. for
  the whole simulation period).

On the other hand, you can also choose a Cluster load where you can add multiple loads together. Be careful however
when mixing hourly and monthly loads!

All building load classes also have the option to add a yearly domestic hot water (DHW) demand and require you to define
an efficiency for heating, cooling (and optionally DHW) (cf. supra).

Please note that it is possible to add your own load types by inheriting the attributes from the abstract _LoadData,
_HourlyLoad, _LoadDataBuilding and _HourlyLoadBuilding classes.

## Simple example

To show how all the pieces of GHEtool work together, below you can find a step-by-step example of how, traditionally,
one would work with GHEtool.
Start by importing all the relevant classes. In this case we are going to work with a ground model which assumes a
constant ground temperature (e.g. from a TRT-test),
and we will provide the load with a monthly resolution.

```Python
from GHEtool import Borefield, GroundDataConstantTemperature, MonthlyGeothermalLoadAbsolute
```

After importing the necessary classes, the relevant ground data parameters are set.

```Python
data =
GroundDataConstantTemperature(3,  # ground thermal conductivity (W/mK)
                              10,  # initial/undisturbed ground temperature (deg C)
                              2.4 * 10 ** 6)  # volumetric heat capacity of the ground (J/m3K) 
```

Furthermore, for our loads, we need to set the peak loads as well as the monthly base loads for extraction and
injection.

```Python
peak_injection = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak injection in kW
peak_extraction = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak extraction in kW

monthly_load_extraction = [46500.0, 44400.0, 37500.0, 29700.0, 19200.0, 0.0, 0.0, 0.0, 18300.0, 26100.0, 35100.0,
                           43200.0]  # in kWh
monthly_load_injection = [4000.0, 8000.0, 8000.0, 8000.0, 12000.0, 16000.0, 32000.0, 32000.0, 16000.0, 12000.0, 8000.0,
                          4000.0]  # in kWh

# set load object
load = MonthlyGeothermalLoadAbsolute(monthly_load_extraction, monthly_load_injection, peak_extraction, peak_injection)

```

Next, we create the borefield object in GHEtool and set the temperature constraints and the ground data.
Here, since we do not use a pipe and fluid model (
see [Examples](https://ghetool.readthedocs.io/en/stable/sources/code/examples.html) if you need examples were no
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