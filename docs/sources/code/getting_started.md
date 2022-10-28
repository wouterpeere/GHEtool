# Getting started

## Requirements
This code is tested with Python 3.8 (and higher) and requires the following libraries

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

## Installation

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