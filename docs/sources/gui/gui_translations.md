# How to add or correct translations?

Translations for the GUI can be added in a new column in the 
[.\GHEtool\gui\Translations.csv](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/Translations.csv) file. Correction can be made there as well. 
Important is that the seperator in the CSV-file is not comma but semicolon `;`.
Also, an icon and shortcut can be linked there. An explanation how to add an icon can be found in`How to add an icon?`. 
The name of the variable to be translated is shown in column 1 and afterwards the different translations. 
The variable's name is the name in the 
[.\GHEtool\gui\gui_structure.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_structure.py)
or 
[.\GHEtool\gui\gui_window.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_window.py) 
script. Options with multiple inputs are created by separated the different inputs with comma `,`. 
So for an ListBox this can seem like this: 
```
option_list;Option of list,First Option,Second Option;Optionen der Liste,Erste Option,Zweite Option
```

Afterwards the [.\GHEtool\gui\translation_csv_to_py.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/translation_csv_to_py.py) script needs 
to be run. This will add the changes to the `Translations` class in `./GHEtool/gui/translation_class.py`.

Now the translation or correction is available in the GUI.