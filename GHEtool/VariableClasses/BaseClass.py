"""
This document contains the information for the BaseClass.
This class is used as a super class for different variable classes.
"""
import numpy as np
from typing import List

from pygfunction.boreholes import Borehole


class BaseClass:
    """
    This class contains basic functionality of different classes within GHEtool.
    It contains the code to generate a dictionary from the class (in order to be able to export to JSON),
    to load a class based on a dictionary and to check whether or not all attributes differ from None.

    This class should only be altered whenever a highly general method should be implemented.
    """
    def _to_dict(self) -> dict:
        """
        This function converts the class variables to a dictionary so it can be saved in a JSON format.
        Currently, it can handle np.ndarray, list, set, str, int, float, tuple,
        pygfunction.Borehole and classes within GHEtool.

        Returns
        -------
        dict
            Dictionary with all the attributes of the class
        """

        # get all variables in class
        if hasattr(self, "__slots__"):
            variables: List[str] = list(self.__slots__)
        else:
            variables: List[str] = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        # initiate dictionary
        dictionary: dict = dict([])

        # populate dictionary
        for key in variables:
            if isinstance(getattr(self, key), (int, bool, float, str)):
                dictionary[key] = getattr(self, key)
                continue

            if isinstance(getattr(self, key), tuple):
                dictionary[key] = {"value": list(getattr(self, key)), "type": "tuple"}
                continue

            if isinstance(getattr(self, key), np.ndarray):
                dictionary[key] = {"value": getattr(self, key).tolist(), "type": "np.ndarray"}
                continue

            if isinstance(getattr(self, key), set):
                dictionary[key] = {"value": list(getattr(self, key)), "type": "set"}
                continue

            if isinstance(getattr(self, key), list):
                if np.any(getattr(self, key)) and isinstance(getattr(self, key)[0], Borehole):
                    # pygfunction object
                    dictionary[key] = {"value": [{key: value for key, value in borehole.__dict__.items()
                                                  if key != "_is_tilted"}
                                                 for borehole in getattr(self, key)],
                                       "type": "pygfunction.Borehole"}
                    continue
                dictionary[key] = getattr(self, key)

            if isinstance(getattr(self, key), dict):
                # note that this can cause problems whenever self.key contains values that or not int, bool, float or str
                dictionary[key] = getattr(self, key)
                continue

            # for all self-defined classes
            if hasattr(getattr(self, key), "_to_dict"):
                dictionary[key] = getattr(self, key)._to_dict()

        return dictionary

    def _from_dict(self, dictionary: dict) -> None:
        """
        This function converts the dictionary values to the class attributes.
        Currently, it can handle np.ndarray, list, set, str, int, float, tuple, pygfunction.Borehole
        and classes within GHEtool.

        Parameters
        ----------
        dictionary
            Dictionary with all the attributes of the class

        Returns
        -------
        None
        """
        for key, value in dictionary.items():

            # for all self-defined classes
            if hasattr(getattr(self, key), "_to_dict"):
                getattr(self, key)._from_dict(value)
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
                    if type == "pygfunction.Borehole":
                        borefield = [Borehole(H=borehole["H"],
                                              D=borehole["D"],
                                              r_b=borehole["r_b"],
                                              x=borehole["x"],
                                              y=borehole["y"],
                                              tilt=borehole["tilt"],
                                              orientation=borehole["orientation"])
                                     for borehole in _value]
                        setattr(self, key, borefield)
                        continue
                # normal dictionary
                setattr(self, key, value)

    def check_values(self) -> bool:
        """
        This functions checks if the class attributes differ from None.

        Returns
        -------
        bool
            True if all values are correct. False otherwise
        """
        # get all variables in class
        if hasattr(self, "__slots__"):
            variables: List[str] = list(self.__slots__)
        else:
            variables: List[str] = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        for var in variables:
            if getattr(self, var) is None:
                return False
        return True
