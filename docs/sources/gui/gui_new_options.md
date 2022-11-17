# How to add new options in the GUI?
The GUI is based on pages which consists of categories which consists of options. 
An example for a page is the borehole resistance page. Here the fluid data category can be found. 
This category has a double spin box option to set the mass flow rate.
The order in which the options are put in the gui_structure.py document is also the order in which they will appear in the GUI itself
(and with the correct tab order).

On this page, one can find how one can create a page, an aim and a category - the structural elements.
Then, the different options (float box, integer box, button box, list box, filename, function button and hint) are explained.
This page ends with an explanation

## Structural elements
All the objects below (being pages, aims and categories) serve as the backbone of the GUI and can hence be interpreted as structural elements.

### Page
To create a page the Page class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous pages or set to `default_parent`.
As second option the name of the page can be set. In the example below `Example page`.
The third option is the button name for the page. In the example below `Name of\nthe button`. The `\n` can be used to create a new line.
The last option is the icon. In this case `:/icons/icons/example_icon.svg`. An explanation how to add an icon can be found here: {ref}`How to add an icon?`.
Furthermore, the next and previous page can be set by using `set_previous_page()` or `set_next_page()`.

```python
from GHEtool.gui.gui_classes import Page
page_example = Page(
    name='Example page',
    button_name='Name of\nthe button',
    icon=":/icons/icons/example_icon.svg",
)
page_example.set_previous_page(page_previous)
page_example.set_next_page(page_next)
```

Example Page
![Python Logo](_static/Example_Page.PNG)

### Aim

To create an aim the Aim class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous aims or set to `default_parent`.
As second option the name of the aim can be set. In the example below `Example aim`.
The third option is the icon. In this case `:/icons/icons/example_icon.svg`. An explanation how to add an icon can be found here: {ref}`How to add an icon?`.
The last option is the page where the aim should be located. In this case `page_aim`. 
An option, which should be show and disappear if the aim is selected or not can be added using `add_link_2_show()`. 
This can be an option, hint, category or function button.

```python
from GHEtool.gui.gui_classes import Aim

aim_example = Aim(
    label='Example aim',
    icon=":/icons/icons/example_icon.svg",
    page=page_aim,
)
aim_example.add_link_2_show(option=option_example)
```

Example Aim
![Python Logo](_static/Example_Aim.PNG)

### Category

To create a category the Category class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous categories or set to `default_parent`.
As second option the name of the category can be set. In the example below `Example category`.
The last option is the page where the category should be located. In this case `page_example`. 

```python
from GHEtool.gui.gui_classes import Category
category_example = Category(
    label='Example category', 
    page=page_example,
)
```

Example Category
![Python Logo](_static/Example_Category.PNG)

## Option elements
In this section, all different option elements will be discussed. These are elements that can be used to set values (or show them).

### Float box

To create a float box the FloatBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to `default_parent`.
As second option the name of the float box can be set. In the example below `Float label text`.
The next option is a default value. In this case `0.5`.
The next option is the category which should contain the option. In this case `category_example`.
The next option is the decimal position (0=1, 4=1.2345). In this case `2`.
The next option is a minimal value. In this case `0`.
The next option is a maximal value. In this case `1`.
The next option is a step value in which the value is increased if the arrows of the box are used. 
In this case `0.1`.
The function `add_link_2_show()` can be used to couple the float value to other options, hints, function buttons or categories. 
So in the example `option_linked` will be shown if the float value is below 0.1 or above 0.9.


```python
from GHEtool.gui.gui_classes import FloatBox
option_float = FloatBox(
    label='Float label text', 
    default_value=0.5, 
    category=category_example,
    decimal_number=2,
    minimal_value=0, 
    maximal_value=1,
    step=0.1,
)
option_float.add_link_2_show(option=option_linked, below=0.1, above=0.9)
```

Example float box
![Python Logo](_static/Example_Float_Box.PNG)

### Integer box

To create a integer box the IntegerBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to `default_parent`.
As second option the name of the integer box can be set. In the example below `Int label text`.
The next option is a default value. In this case `2`.
The next option is the category which should contain the option. In this case `category_example`.
The next option is a minimal value. In this case `0`.
The next option is a maximal value. In this case `12`.
The next option is a step value in which the value is increased if the arrows of the box are used. 
In this case `2`.
The function `add_link_2_show()` can be used to couple the integer value to other options, hints, function buttons or categories. 
So in the example `option_linked` will be shown if the integer value is below 1 or above 10.

```python
from GHEtool.gui.gui_classes import IntBox
option_int = IntBox(
    label='Int label text', 
    default_value=2, 
    category=category_example,
    minimal_value=0, 
    maximal_value=12,
    step=2,
)
option_int.add_link_2_show(option=option_linked, below=1, above=10)
```

Example integer box
![Python Logo](_static/Example_Int_Box.PNG)

### Button box

To create a button box the ButtonBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to `default_parent`.
As second option the name of the button box can be set. In the example below `Button box label text`.
The next option is a default index. In this case `0`.
The next option are the entries. In this case `Option 1, Option 2`.
The next option is the category which should contain the option. In this case `category_example`.
The function `add_link_2_show()` can be used to couple the selected index to other options, hints, function buttons or categories. 
So in the example `option_linked` will be shown if the first (`0`) option is selected.

```python
from GHEtool.gui.gui_classes import ButtonBox

option_buttons = ButtonBox(
    label='Button box label text',
    default_index=0,
    entries=['option 1', 'option 2'],
    category=category_example,
)
option_buttons.add_link_2_show(option=option_linked, on_index=0)
```

Example button box
![Python Logo](_static/Example_Button_Box.PNG)

### List box

To create a list box the ListBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous options or set to `default_parent`.
As second option the name of the list box can be set. In the example below `List box label text`.
The next option is a default index. In this case `0`.
The next option are the entries. In this case `Option 1, Option 2`.
The next option is the category which should contain the option. In this case `category_example`.
The function `add_link_2_show()` can be used to couple the selected index to other options, hints, function buttons or categories. So in the example 
`option_linked` will be 
shown if the 
first (`0`) option is selected.

```python
from GHEtool.gui.gui_classes import ListBox
option_list = ListBox(
    label='List box label text',
    default_index=0,
    entries=['Option 1', 'Option 2'],
    category=category_example,
)
option_list.add_link_2_show(option=option_linked, on_index==0)
```

Example list box
![Python Logo](_static/Example_List_Box.PNG)

### Filename

To create a filename box the FileNameBox class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous file name boxes or set to `default_parent`.
As second option the name of the file name box can be set. In the example below `File name box label text`.
The next option is a default filename. In this case `example_file.XX`.
The next option is the dialog text which will be shown if the button to select a file is selected. In this case `Choose *.XX file`.
The next option is the error message if no file is found/selected. In this case `no file found`.
This error message will be displayed in the statusbar so the status bar object has to be provided. In this example `status_bar`. 
The last option is the category which should contain the option. In this case `category_example`.

```python
from GHEtool.gui.gui_classes import FileNameBox
option_file = FileNameBox(
    label='File name box label text',
    default_value='example_file.XX',
    dialog_text='Choose *.XX file',
    error_text='no file found',
    status_bar=status_bar,
    category=category_example,
)
```

Example filename box
![Python Logo](_static/Example_Filename.PNG)

### Function button

To create a function button the FunctionButton class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous file function buttons or set to `default_parent`.
As second option the name of the button text can be set. In the example below `Press Here to activate function`.
The next option is the icon. In this case `:/icons/icons/example_icon.svg`. An explanation how to add an icon can be found here: {ref}`How to add an icon?`.
The last option is the category which should contain the option. In this case `category_example`.
The button can be linked to a function using `change_event()`. In this case every time the button is clicked the `function_to_be_called()` is activated.

```python
from GHEtool.gui.gui_classes import FunctionButton
function_example = FunctionButton(
    button_text='Press Here to activate function',
    icon=':/icons/icons/example_icon.svg',
    category=category_example,
)
function_example.change_event(function_to_be_called())
```

Example function button
![Python Logo](_static/Example_Function_Button.PNG)

### Hint

To create a hint the Hint class has to be imported from 
[.\GHEtool\gui\gui_classes.py](https://github.com/wouterpeere/GHEtool/blob/main/GHEtool/gui/gui_classes.py).
Then a default widget parent has to be set. This can be just copied from the previous hints or set to `default_parent`.
As second option the hint can be set. In the example below `This is a hint to something important.`.
The next option is the category which should contain the option. In this case `category_example`.
The last option is a boolean to set if the hint is a warning or not. In this case it is (`True`). So the hint will be display in a yellow and not white text 
color.

```python
from GHEtool.gui.gui_classes import Hint
hint_example = Hint(
    hint='This is a hint to something important.',
    category=category_example,
    warning=True,
)
function_example.change_event(function_to_be_called())
```

Example Hint
![Python Logo](_static/Example_Hint.PNG)

## Result elements
Finally, there is a specific type of elements for the GUI related to the results. These are explained here.

### Figure results

### Text results