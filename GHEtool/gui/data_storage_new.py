from GHEtool.gui.gui_structure import GuiStructure
import pandas as pd


class DataStorageNew:

    def __init__(self, gui_structure: GuiStructure):
        for option, name in gui_structure.list_of_options:
            setattr(self, name, option.get_value())
        for aim, name in gui_structure.list_of_aims:
            setattr(self, name, aim.widget.isChecked())

    def set_values(self, gui_structure: GuiStructure):
        for option, name in gui_structure.list_of_options:
            option.set_value(getattr(self, name))
        for aim, name in gui_structure.list_of_aims:
            aim.widget.setChecked(getattr(self, name))

    def save(self):
        data = pd.DataFrame([(name, getattr(self, name)) for name in self.__dict__])
        data.to_csv('test.csv')
