# GHEtool's Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [unreleased]

nothing

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

[Unreleased]: https://github.com/wouterpeere/GHEtool/compare/v2.0.5...main
[2.0.5]: https://github.com/wouterpeere/GHEtool/compare/v2.0.4...v2.0.5
[2.0.4]: https://github.com/wouterpeere/GHEtool/compare/v2.0.3...v2.0.4
[2.0.3]: https://github.com/wouterpeere/GHEtool/compare/v2.0.2...v2.0.3
[2.0.2]: https://github.com/wouterpeere/GHEtool/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/wouterpeere/GHEtool/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/wouterpeere/GHEtool/compare/v1.0.1...v2.0.0
[1.0.1]: https://github.com/wouterpeere/GHEtool/releases/tag/v1.0.1
