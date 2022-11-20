# How to add an icon?

An Icon can be added to the gui by adding `example_icon.svg` icon to `icons.qrc` file and locating in the icon in the icons folder:

```xml
<file>icons/example_icon.svg</file>
```

Afterwards the `icons_rc.py` has to be recompiled using the following command line:

```
pyside6-rcc ./GHEtool/gui/icons.qrc -o ./GHEtool/gui/icons_rc.py
```

Now the icon can be used in the GUI.
