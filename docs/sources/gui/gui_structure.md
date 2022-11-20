# General structure of the GUI
When looking in the [gui folder](https://github.com/wouterpeere/GHEtool/tree/main/GHEtool/gui) on the GitHub page, one will find a couple of documents that together make the gui work. In this section, the general structure of the GUI will be explained.

## start_gui.py
This file does nothing but to start the gui. When creating a new GUI version, please update the version in this document as well.

## gui_base_classes.py
This document should normally not be altered. It contains some general information about the used color schemes etc.

## gui_classes.py
All of the elements you can use on the GUI (the buttons, text inputs etc.) have been defined in this document.
Everything related to the behaviour of the different elements used in *gui_structure.py* can be found and changed here.
This class is only needed when one wants to change the general behaviour of an element.

## gui_structure.py
This document is the center of the GUI. It contains in order all the different elements that appear inside the GUI and the relationship between them.
Adding new options to the GUI, will be done here.

The GUI is based on pages which consists of categories which consists of options.
An example for a page is the borehole resistance page. Here the fluid data category can be found.
This category has a double spin box option to set the mass flow rate.
The order in which the options are put in the *gui_structure.py* document is also the order in which they will appear in the GUI itself (and with the correct tab order).

For more information about all the elements one can use for the GUI, please look at the modules page.

## gui_data_structure.py
This document makes sure that all the elements, put in the gui_structure, will be saved when the gui is used. It stores all the values of the gui in a variable (which will then later be dumped into an *.GHEtool file).
This document also adds some extra variables to the ones comming from the gui_structure. For example, when entering monthly loads, every month is a variable and will also be saved as such. However, inside the datastorage class, a new variable is created to combine all these different monthly variables into one in order to make life easier.
One can hence also create variables here that can be useful for the calculation itself.

## gui_calculation_thread.py
This document is the core of the GUI when it comes to the real calculation. In the function _run_ one defines the functionality of the GUI. For each aim (cf. infra), one creates a borefield object and does some calculations to it.
Here, all the variables from gui_structure can be used by using *self.DS.NameOfTheGuiStructureVariable*. Also, variables directly created inside the datastorage class can be used here.

## gui_combine_window.py
This document creates the GUI itself. It makes sure that all the elements (defined in *gui_structure.py*) are placed correctly, and that all the navigation works.

## translation_class.py
This document is automatically created and takes care of different translations for the gui. For more information, see the section about translations.