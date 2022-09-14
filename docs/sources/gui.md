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

## How to add new options in the GUI?

New options can be added in the 
[.\GHEtool\gui\gui_structure.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_structure.py)
script. The added options will be automatically integrated in the Datastorage and the GUI.
The following sections will explain the gui structure and the different options which can be added.

The implemented options can then be used in the CalcProblem class in the 
[.\GHEtool\gui\gui_calculation_thread.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_calculation_thread.py) 
script. The value of the option get be get by the `get_value()` function.

### GUI structure

The GUI is based on pages which consists of categories which consists of options. 
An example for a page is the borehole resistance page. Where the fluid data category can be found. 
This category has a double spin box option to set the mass flow rate.

### Page

To create a page the Page class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous pages or set to ´default_parent´.
As second option the name of the page can be set. In the example below `Example page`.
The third option is the button name for the page. In the example below `Name of\nthe button`. The `\n` can be used to create a new line.
The last option is the icon. In this case `:/icons/icons/example_icon.svg`. An explanation how to add an icon can be found here: {ref}`How to add an icon?`.
Furthermore, the next and previous page can be set by using `set_previous_page()` or `set_next_page()`.

```python
from GHEtool.gui.gui_classes import Page
page_example = Page(
    default_parent=default_parent, 
    name='Example page',
    button_name='Name of\nthe button',
    icon=":/icons/icons/example_icon.svg",
)
page_example.set_previous_page(page_previous)
page_example.set_next_page(page_next)
```

### Aim

To create an aim the Aim class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous aims or set to ´default_parent´.
As second option the name of the aim can be set. In the example below `Example aim`.
The third option is the icon. In this case `:/icons/icons/example_icon.svg`. An explanation how to add an icon can be found here: {ref}`How to add an icon?`.
The last option is the page where the aim should be located. In this case `page_aim`. 
An option, which should be show and disappear if the aim is selected or not can be added using `add_linked_option()`. 
This can be an option, hint, category or function button. 

```python
from GHEtool.gui.gui_classes import Aim
aim_example = Aim(
    default_parent=default_parent, 
    label='Example aim',
    icon=":/icons/icons/example_icon.svg",
    page=page_aim,
)
aim_example.add_linked_option(option=option_example)
```

### Category

To create a category the Category class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous categories or set to ´default_parent´.
As second option the name of the category can be set. In the example below `Example category`.
The last option is the page where the category should be located. In this case `page_example`. 

```python
from GHEtool.gui.gui_classes import Category
category_example = Category(
    default_parent=default_parent, 
    label='Example category', 
    page=page_example,
)
```


### Float box

To create a float box the FloatBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to ´default_parent´.
As second option the name of the float box can be set. In the example below `Float label text`.
The next option is a default value. In this case `0.5`.
The next option is the category which should contain the option. In this case `category_example`.
The next option is the decimal position (0=1, 4=1.2345). In this case `2`.
The next option is a minimal value. In this case `0`.
The next option is a maximal value. In this case `1`.
The next option is a step value in which the value is increased if the arrows of the box are used. 
In this case `0.1`.


```python
from GHEtool.gui.gui_classes import FloatBox
option_float = FloatBox(
    default_parent=default_parent, 
    label='Float label text', 
    default_value=0.5, 
    category=category_example,
    decimal_number=2,
    minimal_value=0, 
    maximal_value=1,
    step=0.1,
)
```

### Integer box

To create a integer box the IntegerBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to ´default_parent´.
As second option the name of the integer box can be set. In the example below `Int label text`.
The next option is a default value. In this case `2`.
The next option is the category which should contain the option. In this case `category_example`.
The next option is a minimal value. In this case `0`.
The next option is a maximal value. In this case `12`.
The next option is a step value in which the value is increased if the arrows of the box are used. 
In this case `2`.

```python
from GHEtool.gui.gui_classes import IntBox
option_int = IntBox(
    default_parent=default_parent, 
    label='Int label text', 
    default_value=2, 
    category=category_example,
    minimal_value=0, 
    maximal_value=12,
    step=2,
)
```

### Button box

To create a button box the ButtonBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to ´default_parent´.
As second option the name of the button box can be set. In the example below `Button box label text`.
The next option is a default index. In this case `0`.
The next option are the entries. In this case `Option 1, Option 2`.
The next option is the category which should contain the option. In this case `category_example`.
The function `add_linked_option()` can be used to couple the selected index to other options, hints, function buttons or categories. 
So in the example `option_linked` will be shown if the 
first (`0`) option is selected.

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

To create a list box the ListBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to ´default_parent´.
As second option the name of the list box can be set. In the example below `List box label text`.
The next option is a default index. In this case `0`.
The next option are the entries. In this case `Option 1, Option 2`.
The next option is the category which should contain the option. In this case `category_example`.
The function `add_linked_option()` can be used to couple the selected index to other options, hints, function buttons or categories. So in the example 
`option_linked` will be 
shown if the 
first (`0`) option is selected.

```python
from GHEtool.gui.gui_classes import ListBox
option_list = ListBox(
    default_parent=default_parent,
    label='List box label text',
    default_index=0,
    entries=['Option 1', 'Option 2'],
    category=category_example,
)
option_list.add_linked_option(option=option_linked, index=0)
```

### Filename

To create a filename box the FileNameBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous file name boxes or set to ´default_parent´.
As second option the name of the file name box can be set. In the example below `File name box label text`.
The next option is a default filename. In this case `example_file.XX`.
The next option is the dialog text which will be shown if the button to select a file is selected. In this case `Choose *.XX file`.
The next option is the error message if no file is found/selected. In this case `no file found`.
This error message will be displayed in the statusbar so the status bar object has to be provided. In this example `status_bar`. 
The last option is the category which should contain the option. In this case `category_example`.

```python
from GHEtool.gui.gui_classes import FileNameBox
option_file = FileNameBox(
    default_parent=default_parent,
    label='File name box label text',
    default_value='example_file.XX',
    dialog_text='Choose *.XX file',
    error_text='no file found',
    status_bar=status_bar,
    category=category_example,
)
```

### Function button

To create a function button the FunctionButton class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous file function buttons or set to ´default_parent´.
As second option the name of the button text can be set. In the example below `Press Here to activate function`.
The next option is the icon. In this case `:/icons/icons/example_icon.svg`. An explanation how to add an icon can be found here: {ref}`How to add an icon?`.
The last option is the category which should contain the option. In this case `category_example`.
The button can be linked to a function using `change_event()`. In this case every time the button is clicked the `function_to_be_called()` is activated.

```python
from GHEtool.gui.gui_classes import FunctionButton
function_example = FunctionButton(
    default_parent=default_parent,
    button_text='Press Here to activate function',
    icon=':/icons/icons/example_icon.svg',
    category=category_example,
)
function_example.change_event(function_to_be_called())
```

### Hint

To create a hint the Hint class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous hints or set to ´default_parent´.
As second option the hint can be set. In the example below `This is a hint to something important.`.
The next option is the category which should contain the option. In this case `category_example`.
The last option is a boolean to set if the hint is a warning or not. In this case it is (`True`). So the hint will be display in a yellow and not white text 
color.

```python
from GHEtool.gui.gui_classes import Hint
function_example = Hint(
    default_parent=default_parent,
    hint='This is a hint to something important.',
    category=category_example,
    warning=True,
)
function_example.change_event(function_to_be_called())
```


## How to add or correct translations?

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
