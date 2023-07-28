# General structure of the GUI
A lot of methods and functionalities of the GUI are happening in the background, since everything is built on top of [ScenarioGUI](https://github.com/tblanke/ScenarioGUI).
When looking in the [gui folder](https://github.com/wouterpeere/GHEtool/tree/main/GHEtool/gui) on the GitHub page, one will find a couple of documents that are needed in order to make the gui work. In this section, the general structure of the GUI will be explained.

## start_gui.py
This file does nothing but to start the gui. When creating a new GUI version, please update the version in this document as well.

## gui_structure.py
This document is the center of the GUI. It contains in order all the different elements that appear inside the GUI and the relationship between them.
Adding new options to the GUI, will be done here.

The GUI is based on pages which consists of categories which consists of options.
An example for a page is the borehole resistance page. Here the fluid data category can be found.
This category has a double spin box option to set the mass flow rate.
The order in which the options are put in the *gui_structure.py* document is also the order in which they will appear in the GUI itself (and with the correct tab order).

For more information about all the elements one can use for the GUI, please look at the modules page.

## data_2_borefield_func.py
Where the previous document is the core of the GUI itself, this document contains all the data handling and actual communication with the core modules of GHEtool.
Here, one converts all the data inputted in the gui_structure to data formats that can be processed by GHEtool. All methods and functionalities of the tool
are inputted here and are automatically handled in the background by the multi-threaded processing of [ScenarioGUI](https://github.com/tblanke/ScenarioGUI).

## gui_config.ini
This file contains general information the [ScenarioGUI](https://github.com/tblanke/ScenarioGUI) needs to be able
to create the GUI of GHEtool with the right location of icons, color scheme etc.

## translation_class.py
This document is automatically created and takes care of different translations for the gui. For more information, see the section about translations.