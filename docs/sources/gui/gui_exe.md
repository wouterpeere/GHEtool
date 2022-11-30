# How to create the *.exe file?

The exe can be created using [PyInstaller](https://pyinstaller.org/en/stable/).

The following line will create a windowed version of the executable. Ideally, you have forked GHEtool into a project with its own virtual python environment.

```
python -m PyInstaller --noconfirm --onefile --windowed --splash "./GHEtool/gui/icons/Icon.ico" --name "GHEtool" --icon "./GHEtool/gui/icons/Icon.ico" "./GHEtool/gui/start_gui.py"
```
The following line will create a version which also displays a windows console with error messages of the executable. 
``` 
python -m PyInstaller --noconfirm --onefile --console --splash "./GHEtool/gui/icons/Icon.ico" --name "GHEtool_with_command_line" --icon "./GHEtool/gui/icons/Icon.ico" "./GHEtool/gui/start_gui.py"
```

The setup *.exe can be created using the *.iss files in the GHEtool/gui folder. Therefore, the LinkToGHEtool (line 4) has to be changed to the current one. 
Afterwards [InnoSetup](http://www.innosetup.org/) can use the *.iss file to create the setup *.exe file. 
The "Inno_setup_console.iss" file is creating a setup for a GHEtool implementation with a windows console and "Inno_setup_windowed.iss" a normal version. 
