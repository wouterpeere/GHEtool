# How to create the *.exe file?

The creation of an *.exe file consists of three steps:

1. Set up a fresh virtual environment
2. Create executable folder using py-installer
3. Create GHEtools installable using InnoSetup

## Set up a fresh virtual environment

A new virtual environment can be created at the `venv` folder using the following command in the command line:

```
python -m venv venv
venv\Scripts\activate.bat
```

or if a virtual environment already exists all packages can be uninstalled either using the following command:

```
pip freeze | xargs pip uninstall -y
```

or these commands:

```
pip freeze > req.txt
pip uninstall -r req.txt -y
del req.txt
```
Afterwards the required packages and pyinstaller have to be installed using the following commands:

```
python -m pip install -r requirements.txt
python -m pip install PyInstaller
```

## Create executable folder using py-installer

The exe-folder can be created using [PyInstaller](https://pyinstaller.org/en/stable/). The following line will create a windowed version of the executable.

```
python -m PyInstaller  "./GHEtool/gui/GHEtool.spec" --noconfirm
```
The following line will create a version which also displays a windows console with error messages of the executable. 
``` 
python -m PyInstaller  "./GHEtool/gui/GHEtool_with_command_line.spec" --noconfirm
```

## Create GHEtools installable using InnoSetup

The setup *.exe can be created using the *.iss files in the GHEtool/gui folder. Therefore, the LinkToGHEtool (line 4) has to be changed to the current one. 
Afterwards [InnoSetup](http://www.innosetup.org/) can use the *.iss file to create the setup *.exe file. 
The "Inno_setup_console.iss" file is creating a setup for a GHEtool implementation with a windows console and "Inno_setup_windowed.iss" a normal version. 

## Create the DMG for MAC

Follow the steps as before but run the following pyinstaller command instead. The InnoSetup step is skipped as well.

``` 
python -m PyInstaller  "./GHEtool/gui/GHEtool_mac.spec" --noconfirm
```

Instead of the InnoSetup step the dmgbuild package can be used by installing it using pip ("pip install dmgbuild")
And afterwards running the following command:

``` 
python -m dmgbuild -s ./GHEtool/gui/mac_settings.py "GHEtool" GHEtool.dmg
```