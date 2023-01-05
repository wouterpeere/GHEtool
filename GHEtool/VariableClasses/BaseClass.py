import numpy as np


class BaseClassVariables:
    """
    This class is the base class
    """
    def __to_dict__(self) -> dict:
        """
        This function converts the class variables to a dictionary so it can be saved in a JSON format.
        Currently, it can handle np.ndarray, list, set, str, int, float, tuple and classes within GHEtool.

        Returns
        -------
        dict
            Dictionary with all the attributes of the class
        """

        # get all variables in class
        if hasattr(self, "__slots__"):
            variables: list = self.__slots__
        else:
            variables: list = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        # initiate dictionary
        dictionary: dict = dict([])

        # populate dictionary
        for key in variables:
            if isinstance(getattr(self, key), (int, bool, float, str, list)):
                dictionary[key] = getattr(self, key)

            if isinstance(getattr(self, key), tuple):
                dictionary[key] = {"value": list(getattr(self, key)), "type": "tuple"}

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

    def __from_dict__(self, dictionary: dict) -> None:
        """
        This function converts the dictionary values to the class attributes.
        Currently, it can handle np.ndarray, list, set, str, int, float, tuple and classes within GHEtool.

        Parameters
        ----------
        dict
            Dictionary with all the attributes of the class

        Returns
        -------
        None
        """
        for key, value in dictionary.items():

            # for all self-defined classes
            if hasattr(getattr(self, key), "__to_dict__"):
                getattr(self, key).__from_dict__(value)
                continue

            if isinstance(value, (int, bool, float, str, list)):
                setattr(self, key, value)
                continue

            if isinstance(value, dict):
                # note that this can mean that the value is a dictionary, or it is a np.ndarray, set or tuple
                keys = value.keys()
                if len(keys) == 2 and "type" in keys and "value" in keys:
                    type = value["type"]
                    _value = value["value"]

                    if type == "set":
                        setattr(self, key, set(_value))
                        continue
                    if type == "np.ndarray":
                        setattr(self, key, np.array(_value))
                        continue
                    if type == "tuple":
                        setattr(self, key, tuple(_value))
                        continue

                # normal dictionary
                setattr(self, key, value)

    def _check_values(self) -> bool:
        """
        This functions checks if the class attributes differ from None.

        Returns
        -------
        bool
            True if all values are correct. False otherwise
        """
        # get all variables in class
        if hasattr(self, "__slots__"):
            variables: list = self.__slots__
        else:
            variables: list = [attr for attr in dir(self) if
                               not callable(getattr(self, attr)) and not attr.startswith("__")]

        for var in variables:
            if getattr(self, var) is None:
                return False
        return True
