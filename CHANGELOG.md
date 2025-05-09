# GHEtool's Changelog and future developments

All notable changes to this project will be documented in this file. For future developments, please visit
our [project board](https://github.com/users/wouterpeere/projects/2) on GitHub.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.3.3] - Unpublished

### Added

- Temperature dependent fluid properties (issue #143).
- Freezing point to fluid data (issue #314).

### Changed

- Changed back-end to be compatible with pygfunction 2.3.0 (issue #345).
- The __repr__ of the different classes. It now returns a dictionary.
- Remove ghe_logger since no longer used.

## [2.3.2] - 2025-04-02

### Added

- Added support for DHW profiles in optimisation (issue #272).
- Support for Python 3.13 (issue #319).
- Added Prandtl number to FluidData class (issue #326).
- Pressure drop calculation for horizontal pipe and total system (issue #332).
- Added optimisation function for balanced borefield (issue #335).
- Min_temperature and Max_temperature property to results class (issue #335).

### Changed

- Added U-bend to the pressure drop calculation of the pipe (issue #332).
- Remove optimise_load_power and optimise_load_energy from Borefield object (issue #332).

### Fixed

- Increase accuracy of optimise load profile (issue #335).
- Problem with MonthlyBuildingLoadMultiYear (issue #339).

## [2.3.1] - 2025-01-23

### Added

- __repr__ for every class (issue #310).
- Added start_depth to calculation of k_s, volumetric_heat_capacity, calculate_value, calculate_Tg and alpha in _
  GroundData (issue #137).
- Added start_depth to the calculation of Tg in all GroundClasses (issue #137).
- Added property 'depth' to Borefield class (issue #137).
- Added function 'calculate_depth' to Borefield class (issue #137).
- Added support for titled boreholes (issue #318).
- Added neural network for faster batch calculations (issue #322).

### Fixed

- Problem with optimise energy profile (issue #306).
- Problem with ground parameters in optimise_energy_profile (issue #317).

### Changed

- Make terminology consistent: borehole length != borehole depth (issue #317).
- _GroundData changed argument of check_depth, k_s, volumetric_heat_capacity, calculate_Tg, calculate_value and alpha
  from 'H' to 'depth' (issue #137).
- Removed 'depth' attribute in optimise load functions, for it is already included in the Borefield object (issue #317).
- Added 'depth' attribute to get_Rb and calculate_Rb functions in the Borehole class (issue #317).
- Changed 'depth' attribute to 'length' in print_temperature_profile_fixed_length, calculate_temperatures (issue #317).

## [2.3.0] - 2024-11-05

### Added

- Added the Separatus probe.
- Extra validation based on the work of Ahmadfard & Bernier (issue #243).
- Added the option to exclude DHW from the peak heating load (issue #252).
- Added vfr to Fluid Class (issue #262).
- Added yearly_heating_load_simulation_period, yearly_cooling_load_simulation_period,
  yearly_heating_peak_simulation_period and yearly_cooling_peak_simulation_period to the Load class (issue #265).
- Added max peak heating/cooling to optimise_load_profile functions (issue #276).
- Added pressure drop across a U-tube (issue #278).
- Efficiency classes for COP, EER, SCOP, SEER (issue #285).
- Added building laod classes (issue #288).
- Added __eq__ method for Result and Efficiency classes (issue #288).
- Added _time_array to building loads (issue #291).
- Added EERCombined for combined active and passive cooling efficiency (issue #291, #296).
- Cluster Class (issue #298).

### Changed

- No longer support of Python 3.8.
- Vfr in FluidData now returns also a value if vfr = None based on the mfr.
- Changed definition of the geothermal load classes to use injection/extraction terminology instead of cooling/heating (
  issue #220).
- Change skopt to Optuna in active_passive_cooling (issue #258).
- Moved plot_load_duration to HourlyLoad class (issue #260).
- Clean up Baseclass (issue #260).
- Removed depreciated 'optimise_load_profile', '_percentage_heating', '_percentage_cooling' from Borefield.py (issue
  #268).
- Removed '_external_load', '_secundary_borefield_load', '_building_load' from Borefield.py (issue #268).
- Added DHW profiles to Building load classes (issue #273).
- Split Results class into ResultsHourly and ResultsMonthly (issue #281).
- Moved implementation of 'optimise_load_profile_power' and 'optimise_load_profile_energy' into a separate document (
  issue #283).
- Removed a couple of log messages (issue #288).
- Optimise load profile works with a variable COP/EER (issue #288).
- Rename cylindrical_correction.py (issue #298).

### Fixed

- Problems with optimise_load_profile_energy (issue #255).
- Fix plot_load_duration (issue #260).
- Problem in CI/CD and testing for python <3.12 (issue #274).
- Fix compatibility with numpy 2.0 (issue #274).
- Fix problem with start month and zero peak loads (issue #288).
- Problem with EERCombined (issue #300).

## [2.2.2] - 2024-05-16

### Added

- Added multiple ground layers (issue #97).
- Function to create box, U and L-shaped borefields (issue #224).
- Multiple year validation for L3 and L4 sizing (issue #227).
- Added MonthlyGeothermalLoadMultiYear (issue #227).
- Added optimise_load_profile_energy (issue #229).
- Added k_p_out to Coaxial Pipe class (issue #239).

### Changed

- Removed set_peak_length from Borefield class (issue #227).
- Definition of the optimise_load_profile_class (issue #229).
- Changed number_of_boreholes to an attribute (issue #233).
- Definition of H when loading a borefield is now the average borehole depth (issue #233).
- Changed store_previous_values in GFunction class to be a property (issue #233).
- Changed temperature database to a json-file (issue #235).
- Changed optimise_load_profile_power to be able to work with hourly data directly (issue #237).
- Renamed main_class.py to borefield.py for consistent naming convention (issue #244).
- Removed parameter 'Tf' from borefield.py since it is no longer needed (issue #249).

### Fixed

- Small typo's in functions (issue #224).
- Bug when using borefield with different borehole lengths (issue #233).

## [2.2.1] - 2024-01-27

### Added

- GHEtool is available on conda-forge (issue #107).
- Possibility to start in another month (issue #140).
- Equal functions for HourlyGeothermalLoad and MonthlyGeothermalLoadAbsolute (issue #189).
- Cylindrical borehole correction (issue #187).
- __add__ functionality for the load classes (issue #202).

### Changed

- Negative reference temperatures for the fluid are now possible (issue #192).
- Move code related to the GUI to a separate repo (issue #210).
- Autorelease to PyPi and testPyPi (issue #212).

### Fixed

- Problem with multiyear hourly data and L3 sizing (issue #153).
- Problem with negative g-function values (issue #187).
- Bug in load-duration curve when not working with optimize load profile (issue #189).
- Bug in hourly data (issue #196).
- Bug in saving after a file has been moved (issue #198).
- Bug in DHW and peak heating power(issue #202).

## [2.2.0] - 2023-10-17

### Added

- Extra warning message if one wants to load a GHEtool file that was created with a newer version.
- Borehole thermal resistance is now visible at the borehole thermal resistance page (issue #51).
- New class of GroundData: GroundTemperatureGradient added (issue #145).
- Load classes (issue #45).
- Pipe classes (single, double, coaxial, Multiple U Tube) (issue #40 and #45).
- Added another methodology for sizing with a variable ground temperature (issue #144).
- Custom error when the field cannot be sized due to a ground temperature gradient (issue #156).
- Interpolation option in calculate function in Gfunction class (issue #159).
- Absolute and relative tolerances for the sizing methods even as a maximum number of iterations is added, so there is
  more transparency and flexibility in the trade-off between accuracy and speed (issue #159).
- Added advanced options to GHEtool GUI (issue #165).
- Added a result class so all calculated temperatures are now in a separate Result class object within the borefield
  object (issue #167).
- Added domestic hot water (DHW) to GHEtool (issue #172).
- Glycol-water mixtures can now be selected from within the GUI (issue #174).
- Pygfunction media object can be imported into the FluidData object in GHEtool (issue #174).
- Temperature and flux database (Europe) implemented (issue #178).
- Yearly heating/cooling load in LoadClass (issue #180).

### Changed

- GUI was moved to a separate project: [ScenarioGUI](https://github.com/tblanke/ScenarioGUI).
- H_init was removed from the sizing functions since it was not used.
- Rb is now solely handled by the borehole object.
- load_hourly_profile is moved to the separate load classes (issue #45).
- Removed 'set_hourly_cooling_load', 'set_hourly_heating_load' from main_class and move it to separate load class (issue
  #45).
- Moved draw_borehole_internals to PipeClass (issue #45).
- Borehole equivalent resistances is now calculated in one step, centralised in the pipe class (issue #45).
- Go to 100% code coverage with 350 tests.
- Threshold interpolation for g-functions set to a relative threshold of 25% relative to the demanded depth (issue
  #144).
- Implemented a custom error for crossing the maximum number of iterations: 'MaximumNumberOfIterations' (issue #144).
- _size_based_on_temperature_profile now returns two arguments: the required depth and a boolean flag to check if the
  field is sized (issue #144).
- Speed up of L3/L4 sizing by halving calculation time due to intermediate checks if the field is sized (issue #144).
- Changed ValueError when the field cannot be sized due to a temperature gradient to the custom
  UnsolvableDueToTemperatureGradient Exception (issue #156).
- Rename SizingSetup class to CalculationSetup class (issue #159).
- Move H_init to CalculationSetup class (issue #159).
- Move use_precalcated_data to CalculationSetup class and rename to: 'use_precalculate_dataset' (issue #159).
- Changed 'set_max_ground_temperature' and 'set_min_ground_temperature' to correct names: '
  set_max_avg_fluid_temperature' and 'set_min_avg_fluid_temperature'
- Changed 'minimal average fluid temperature' to 'minimum average fluid temperature' in GUI (issue #172).
- Max value of SEER is now 1000 (issue #178).

### Fixed

- Fixed problem with L2 sizing, when the peak load was the same in all months (issue #146).
- Small bug in faster g-function calculation solved. When changing the borefield, the previously calculated g-functions
  where not removed.
- When using interpolation for the g-functions, the results could vary a little bit based on the previous sizings. By
  reinstating the H_init parameter, this is solved.
- Borehole internals can no longer overlap in the GUI.
- Optimise load profile crashes with small borefields (issue #180).

## [2.1.2] - 2023-04-28

### Added

- Logger for GHEtool (issue #96).
- Examples are now also in RTD.
- Reynolds number is shown on the result page (issue #112).
- Example for the combination of active and passive cooling (issue #114).
- It is now possible to use building loads (with a SCOP/SEER) instead of ground loads(issue #115).

### Changed

- In figure plotting, the interval[x[i], x[i+1]) now has the value y[i] (instead of y[i-1]).
- Scroll behaviour on the result page (issue #99).
- Changed icon of GHEtool.
- Imbalance changed to property so it can handle hourly loads as well (issue #106).
- Remove recalculation option (issue #109).
- When data is loaded in a two-column format, the button for 'two columns' is set (issue #133).
- GUI doesn't crash anymore when wrong seperator and decimal points are selected when loading a .csv.
- One can now use monthly calculations which do not assume equal month length.

### Fixed

- Sizing doesn't crash when either no heating or cooling load is present (issue #91).
- Wrong heating load in april in GUI (issue #94).
- Results are now cleared when new loads are loaded (issue #106).
- Options for g-function calculations are not working (issue #119).
- Wrong naming aim optimise load profile.
- GHEtool now can start after a crash without removing the backup file.
- Some translations were not correct.
- Solves issue with loading .csv file and optimise load profile (issue #130).
- Figure in optimize load profile keeps getting bigger and bigger (issue #131).
- Problem with sizing with temperature gradients (issue #136).
- Problem solved with calculate_multiple_scenarios.

## [2.1.1] - 2023-01-30

### Added

- Added NavigationToolbar to figure (issue #55).
- Added different peak lengths for heating and cooling separately (issue #72).
- Readable saving format for gui (JSON).
- A super class that contains functions relevant for all GHEtool classes.
- Exe can be installed either locally for one user without admin permission or for all users using admin permission.
- Saved files (*.GHEtool) can be loaded from GHEtool by double click.

### Changed

- Created a class for the custom g-functions (issue #57).
- Created a class for g-function calculation that stores the previously calculated g-values to speed up the iterative
  algorithms (issue #57).
- Created a class for sizing_setup to clean up the code.
  The speed improvement is over a factor 10 for heavy iterative procedures (like optimise load profile). A full speed
  improvement report can be found under:
  code version > speed improvements > v2.1.1.
- The sizing methods themselves are now faster due to the fact that only the first and last year are calculated (issue
  #44). For more info, one can check:
  code version > speed improvements > v2.1.1.
- Faster loading time of the GUI.
- Further documentation for optimise_load_profile functionality.
- Smaller exe-file size by setting up a virtual environment and using a pyinstall folder instead of a single file.

### Fixed

- The hourly_heating_load_on_the_borefield and hourly_cooling_load_on_the_borefield are now correctly calculated.
- When an hourly temperature profile is plotted after an optimise_load_profile optimisation, the hourly load on the
  borefield (and not the entire hourly load) is shown.
- Correct conversion from hourly to monthly load (issue #62).
- Problem with np.float16 when using simulation periodes >80 years due to overflow errors.
- Implemented FIFO-class to prevent cycling in iterative sizing.
- A scenario name cannot occur twice in the scenario list.
- Sometimes some gui options were not shown.
- The drag-and-drop behaviour of the scenario list is fixed (issue #80).
- The renaming of a scenario was not possible (issue #86).
- Problems with borehole internals and pipe overlaps.

## [2.1.0] - 2022-11-30

### Added

- Documentation with ReadTheDocs
- GUI Documentation
- Changelog
- New features in the GUI

### Changed

- GUI workflow to be simpler
- precalculated data is removed
- general speed improvements

### Removed

- size by length and width for it is not compatible with the just-in-time calculation of the g-functions.

## [2.0.6] - 2022-10-07

### Added

- new functionalities for g-function calculation (inherited from pygfunction) are implemented

### Changed

- just-in-time calculation of g-functions is included (and will be expanded later)
- custom borefields can be way faster calculated

### Fixed

- Hyperlinks in PyPi should work now
- Sizing by length and width had problems with temperatures below the minimum temperature

## [2.0.5] - 2022-08-31

### Added

- Hourly sizing method (L4) is implemented
- Hourly plotting method
- Volumetric heat capacity is included in the ground data

### Changed

- Implemented numpy arrays everywhere
- Implemented convolution instead of matrix multiplication
- New implementation for L3 sizing

### Fixed

- No more problems with iteration (L2) and sub 1m depth fields
- Fixed bug in main_functionalities example

### Varia

- New validation document for the effective thermal borehole resistance, comparison with EED

## [2.0.4] - 2022-08-17

### Fixed

- Final JOSS paper update

## [2.0.3] - 2022-08-12

### Added

- Variable ground temperature
- Sizing with dynamic Rb*

### Fixed

- General bug fixes

### Changed

- Sizing setup with more streamlined sizing options

## [2.0.2] - 2022-06-12

### Added

- Included a function (and example) on sizing a borefield by length and width

## [2.0.1] - 2022-06-12

### Added

- Included a pytest document to check if package is correctly installed

## [2.0.0] - 2022-04-01

### Added

- GUI
- Borehole thermal resistance (based on the pygfunction package)

### Changed

- More documentation and examples

## [1.0.1] - 2021-12-11

### Changed

- longer simulation period up to 100 years

### Fixed

- fixed bug in interpolation

[2.3.2]: https://github.com/wouterpeere/GHEtool/compare/v2.3.1...v2.3.2

[2.3.1]: https://github.com/wouterpeere/GHEtool/compare/v2.3.0...v2.3.1

[2.3.0]: https://github.com/wouterpeere/GHEtool/compare/v2.2.2...v2.3.0

[2.2.2]: https://github.com/wouterpeere/GHEtool/compare/v2.2.1...v2.2.2

[2.2.1]: https://github.com/wouterpeere/GHEtool/compare/v2.2.0...v2.2.1

[2.2.0]: https://github.com/wouterpeere/GHEtool/compare/v2.1.2...v2.2.0

[2.1.2]: https://github.com/wouterpeere/GHEtool/compare/v2.1.1...v2.1.2

[2.1.1]: https://github.com/wouterpeere/GHEtool/compare/v2.1.0...v2.1.1

[2.1.0]: https://github.com/wouterpeere/GHEtool/compare/v2.0.6...v2.1.0

[2.0.6]: https://github.com/wouterpeere/GHEtool/compare/v2.0.5...v2.0.6

[2.0.5]: https://github.com/wouterpeere/GHEtool/compare/v2.0.4...v2.0.5

[2.0.4]: https://github.com/wouterpeere/GHEtool/compare/v2.0.3...v2.0.4

[2.0.3]: https://github.com/wouterpeere/GHEtool/compare/v2.0.2...v2.0.3

[2.0.2]: https://github.com/wouterpeere/GHEtool/compare/v2.0.1...v2.0.2

[2.0.1]: https://github.com/wouterpeere/GHEtool/compare/v2.0.0...v2.0.1

[2.0.0]: https://github.com/wouterpeere/GHEtool/compare/v1.0.1...v2.0.0

[1.0.1]: https://github.com/wouterpeere/GHEtool/releases/tag/v1.0.1
