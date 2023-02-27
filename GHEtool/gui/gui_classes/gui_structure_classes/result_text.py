from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

from GHEtool.gui.gui_classes.gui_structure_classes.hint import Hint

if TYPE_CHECKING:  # pragma: no cover
    from GHEtool.gui.gui_classes.gui_structure_classes import Category


class ResultText(Hint):
    """
    This class contains all the functionalities of the ResultText option in the GUI.
    The ResultText option can be used to show text results in the results page.
    """
    def __init__(self, result_name: str, category: Category, prefix: str = "", suffix: str = ""):
        """

        Parameters
        ----------
        result_name : str
            Name of the result (will be overwritten by the result anyway)
        category : Category
            Category in which the ResultText should be placed
        prefix : str
            Prefix which should be put in front of the text result
        suffix : str
            Suffix which should be put after the text result

        Examples
        --------
        The example below show the text result for the borefield depth.

        >>> self.result_text_depth = ResultText("Depth", category=self.numerical_results, prefix="Depth: ", suffix="m")
        >>> self.result_text_depth.text_to_be_shown("Borefield", "H")
        >>> self.result_text_depth.function_to_convert_to_text(lambda x: round(x, 2))

        Gives:

        .. figure:: _static/Example_ResultText.PNG

        """
        super().__init__(result_name, category, warning=False)
        self.class_name: str = ""
        self.var_name: str = ""
        self.prefix: str = prefix
        self.suffix: str = suffix
        self._callable = lambda x: f'{x}'

    def text_to_be_shown(self, class_name: str = "Borefield", var_name: str = "H") -> None:
        """
        This function sets the result that should be shown. It refers to a certain variable (var_name) inside the class class_name.

        Parameters
        ----------
        class_name : str
            The class which contains the variable that should be shown (currently only Borefield)
        var_name : str
            Variable name that should be shown. This should be a variable existing in the class_name Class.

        Returns
        -------
        None

        Examples
        --------
        The function below is used to show the borefield depth (variable H in Borefield class).

        >>> self.result_text_depth.text_to_be_shown("Borefield", "H")
        """
        self.class_name = class_name
        self.var_name = var_name

    def function_to_convert_to_text(self, function: Callable) -> None:
        """
        This function set a function that converts the received data for the results to a text format.

        Parameters
        ----------
        function : Callable
            This is the function which takes some data and converts it into a the correct format

        Returns
        -------
        None

        Examples
        --------
        The example below is a function which rounds the data to two decimal places

        >>> self.result_text_depth.function_to_convert_to_text(lambda x: round(x, 2))
        """
        self._callable = function

    def set_text(self, name: str):
        """
        This function sets the text of the prefix and suffix

        Parameters
        ----------
        name: str
            String with the prefix and suffix text.\n
            These strings are separated by ","

        Returns
        -------
        None
        """
        entry_name: List[str, str] = name.split(',')
        self.prefix = entry_name[0]
        self.suffix = entry_name[1]

    def set_text_value(self, data) -> None:
        """
        This function sets the text of the ResultText.
        This text is the combination of the prefix, the data (converted to string) and a suffix.

        Parameters
        ----------
        data
            Data (which will be processed via function_to_convert_to_text) to be shown in the ResultText.

        Returns
        -------
        None
        """
        super().set_text(f'{self.prefix}{self._callable(data)}{self.suffix}')