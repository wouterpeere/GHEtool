# General structure of the GUI
When looking in the [gui folder](https://github.com/wouterpeere/GHEtool/tree/main/GHEtool/gui) on the GitHub page, one will find a couple of documents that together make the gui work. In this section, the general structure of the GUI will be explained.

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

## gui_combine_window.py
This document creates the GUI itself. It makes sure that all the elements (defined in *gui_structure.py*) are placed correctly, and that all the navigation works.

## translation_class.py
This document is automatically created and takes care of different translations for the gui. For more information, see the section about translations.