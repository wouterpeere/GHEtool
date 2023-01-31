# GHEtool's Changelog and future developments
All notable changes to this project will be documented in this file including planned future developments.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.1.2] - [expected] feb 2023

### Added
- Coaxial pipes
- Variable temperature sizing (at least in the code version)
- Reimplemented size by length and width

### Fixed
- Sizing (L2, L3, L4) with no heating or cooling load does not work (issue #91) 

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
- Created a class for g-function calculation that stores the previously calculated g-values to speed up the iterative algorithms (issue #57).
- Created a class for sizing_setup to clean up the code.
The speed improvement is over a factor 10 for heavy iterative procedures (like optimise load profile). A full speed improvement report can be found under:
code version > speed improvements > v2.1.1.
- The sizing methods themselves are now faster due to the fact that only the first and last year are calculated (issue #44). For more info, one can check:
code version > speed improvements > v2.1.1.
- Faster loading time of the GUI.
- Further documentation for optimise_load_profile functionality.
- Smaller exe-file size by setting up a virtual environment and using a pyinstall folder instead of a single file.

### Fixed
- The hourly_heating_load_on_the_borefield and hourly_cooling_load_on_the_borefield are now correctly calculated.
- When an hourly temperature profile is plotted after an optimise_load_profile optimisation, the hourly load on the borefield (and not the entire hourly load) is shown.
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

[2.1.2]: https://github.com/wouterpeere/GHEtool/compare/v2.1.1...main
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
