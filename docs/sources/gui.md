# Graphical Using Interface (GUI)

<!--sphinx-autobuild docs/ docs/build/html--->

## How to create the *.exe file?

The exe can be created using [PyInstaller](https://pyinstaller.org/en/stable/).

The following line will create a windowed version of the executable:

```
python -m PyInstaller --noconfirm --onefile --windowed --splash "./GHEtool/gui/icons/Icon.ico" --name "GHEtool" --icon "./GHEtool/gui/icons/Icon.ico" "./GHEtool/gui/start_gui.py"
```
The following line will create a version which also displays a windows console with error messages of the executable. 
``` 
python -m PyInstaller --noconfirm --onefile --console --splash "./GHEtool/gui/icons/Icon.ico" --name "GHEtool_with_command_line" --icon "./GHEtool/gui/icons/Icon.ico" "./GHEtool/gui/start_gui.py"
```



## GUI structure

### Page

```python
from GHEtool.gui.gui_classes import Page
page_example = Page(
    default_parent=default_parent, 
    icon=":/icons/icons/example_icon.svg",
    name='Example category',
    button_name='Name of the Button',
)
```

### Aim

```python
from GHEtool.gui.gui_classes import Aim
aim_example = Aim(
    default_parent=default_parent, 
    label='Example category',
    icon=":/icons/icons/example_icon.svg",
    page=page_example,
)
aim_example.add_linked_option(option=option_example)
```

### Category

```python
from GHEtool.gui.gui_classes import Category
category_example = Category(
    default_parent=default_parent, 
    label='Example category', 
    page=page_example,
)
```


### Float box

```python
from GHEtool.gui.gui_classes import FloatBox
option_float = FloatBox(
    default_parent=default_parent, 
    label='Float label text', 
    default_value=0.5, 
    minimal_value=0, 
    maximal_value=1,
    step=0.1,
    decimal_number=2,
    category=category_example,
)
```

### Integer box

```python
from GHEtool.gui.gui_classes import IntBox
option_int = IntBox(
    default_parent=default_parent, 
    label='Int label text', 
    default_value=2, 
    minimal_value=0, 
    maximal_value=12,
    step=2,
    category=category_example,
)
```

### Button box

```python
from GHEtool.gui.gui_classes import ButtonBox

option_buttons = ButtonBox(
    default_parent=default_parent,
    label='Button box label text',
    default_index=0,
    entries=['option 1', 'option 2'],
    category=category_example,
)
option_buttons.add_linked_option(option=option_linked, index=0)
```

### List box

```python
from GHEtool.gui.gui_classes import ListBox

option_list = ListBox(
    default_parent=default_parent,
    label='List box label text',
    default_index=0,
    entries=['option 1', 'option 2'],
    category=category_example,
)
option_list.add_linked_option(option=option_linked, index=0)
```

# How to add or correct translations?

Translations for the GUI can be added in a new column in the 
[.\GHEtool\gui\Translations.csv](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/Translations.csv) file. Correction can be made there as well. 
Important is that the seperator in the CSV-file is not comma but semicolon `;`.
Also, an icon and shortcut can be linked there. An explanation how to add an icon can be found here: {ref}`How to add an icon?`. 
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

Know the translation or correction is available in the GUI.

## How to add an icon?

An Icon can be added to the gui by adding `example_icon.svg` icon to `icons.qrc` file and locating in the icon in the icons folder:

```xml
<file>icons/example_icon.svg</file>
```

Afterwards the `icons_rc.py` has to be recompiled using the following command line:

```
pyside6-rcc ./GHEtool/gui/icons.qrc -o ./GHEtool/gui/icons_rc.py
```

Know the icon can be used in the GUI.
