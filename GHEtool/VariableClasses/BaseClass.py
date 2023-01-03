import numpy as np


class BaseClassVariables:
    """
    This class is the base class
    """
    def __to_dict__(self) -> dict:

        # get all variables in class
        if hasattr(self, "__slots__"):
            variables: list = self.__slots__
        else:
            variables: list = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        # initiate dictionary
        dictionary: dict = dict([])

        # populate dictionary
        for key in variables:
            if isinstance(getattr(self, key), (int, bool, float, str)):
                dictionary[key] = getattr(self, key)

            if isinstance(getattr(self, key), np.ndarray):
                dictionary[key] = {"value": getattr(self, key).tolist(), "type": "np.ndarray"}

            if isinstance(getattr(self, key), set):
                dictionary[key] = {"value": list(getattr(self, key)), "type": "set"}

            if isinstance(getattr(self, key), dict):
                # note that this can cause problems whenever self.key contains values that or not int, bool, float or str
                dictionary[key] = getattr(self, key)

            # for all self-defined classes
            if hasattr(getattr(self, key), "__to_dict__"):
                dictionary[key] = getattr(self, key).__to_dict__()

        return dictionary
