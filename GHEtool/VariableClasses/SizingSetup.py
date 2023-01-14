"""
This document contains the SizingSetup class.
This class contains all the relevant settings for the sizing options
"""
import copy
import numpy as np

from GHEtool.VariableClasses.BaseClass import BaseClass


class SizingSetup(BaseClass):
    """
    This class contains all the settings related to the sizing options.
    """
    def __init__(self, use_constant_Rb: bool = None, use_constant_Tg: bool = None, quadrant_sizing: int = 0,
                 L2_sizing: bool = None, L3_sizing: bool = None, L4_sizing: bool = None):
        """

        Parameters
        ----------
        use_constant_Rb : bool
            True if a constant borehole equivalent resistance (Rb*) value should be used
        use_constant_Tg : bool
            True if a constant Tg value should be used (the geothermal flux is neglected)
        quadrant_sizing : int
            Differs from 0 when a sizing in a certain quadrant is desired.
            Quadrants are developed by (Peere et al., 2021) [#PeereBS]_, [#PeereThesis]_
        L2_sizing : bool
            True if a sizing with the L2 method is needed
        L3_sizing : bool
            True if a sizing with the L3 method is needed
        L4_sizing : bool
            True if a sizing with the L4 method is needed

        References
        ----------
        .. [#PeereBS] Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. (2021) Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021. Brugge (Belgium), 1-3 September 2021. https://doi.org/10.26868/25222708.2021.30180
        .. [#PeereThesis] Peere, W. (2020) Methode voor economische optimalisatie van geothermische verwarmings- en koelsystemen. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.

        """
        self._L2_sizing: bool = True
        self._L3_sizing: bool = False
        self._L4_sizing: bool = False
        self.use_constant_Tg: bool = True
        self.use_constant_Rb: bool = True
        self.quadrant_sizing: int = 0
        self._backup: SizingSetup = None

        # set the variables in this class by passing down the values given in this function
        self._set_sizing_setup(kwargs=locals())

    def update_variables(self, **kwargs) -> None:
        """
        This function updates the variables in the current class.

        Parameters
        ----------
        kwargs
            Keyword arguments with all the variables that need to be changed with the corresponding new values

        Returns
        -------
        None
        """
        self._set_sizing_setup(kwargs)

    def _set_sizing_setup(self, kwargs) -> None:
        """
        This method sets all the variables in the SizingSetup class.
        This is done by looping over all the keywords in the kwargs and setting the corresponding variables
        in this class to the value in the kwargs.
        W.r.t. the sizing methodology, it is checked whether or not this can be set.

        Parameters
        ----------
        kwargs
            All the keyword arguments of the init class or all the variables in the class itself.

        Returns
        -------
        None
        """
        variables = vars(self)
        sizing_vars = set(["L2_sizing", "L3_sizing", "L4_sizing"])

        # set value for sizing method
        # Lx_sizing is for the initialisation of the class
        # _Lx_sizing is for the case a backup is set
        L2_sizing = kwargs.get("L2_sizing") if "L2_sizing" in kwargs else kwargs.get("_L2_sizing")
        L3_sizing = kwargs.get("L3_sizing") if "L3_sizing" in kwargs else kwargs.get("_L3_sizing")
        L4_sizing = kwargs.get("L4_sizing") if "L4_sizing" in kwargs else kwargs.get("_L4_sizing")

        self._check_and_set_sizing(L2_sizing, L3_sizing, L4_sizing)

        # set all the other class variables
        for key, val in kwargs.items():
            if key in variables and key not in sizing_vars:
                if val is not None:
                    self.__setattr__(key, val)

    def _check_and_set_sizing(self, L2_sizing: bool, L3_sizing: bool, L4_sizing: bool) -> None:
        """
        This function checks whether or not the sizing method can be set (i.e. a unique method is requested)
        and sets the according variable to True.

        Parameters
        ----------
        L2_sizing : bool
            True if a sizing with the L2 method is needed
        L3_sizing : bool
            True if a sizing with the L3 method is needed
        L4_sizing : bool
            True if a sizing with the L4 method is needed

        Returns
        -------
        None

        Raises
        ------
        ValueError
            This function raises a value error when more than 1 sizing methodology is set to True
        """
        # check if just one sizing is given
        if np.sum([L2_sizing if L2_sizing is not None else 0, L3_sizing if L3_sizing is not None else 0,
                   L4_sizing if L4_sizing is not None else 0]) > 1:
            raise ValueError("Please check if just one sizing method is chosen!")

        self._set_sizing(L2_sizing, L3_sizing, L4_sizing)

    def _set_sizing(self, L2_sizing: bool = False, L3_sizing: bool = False, L4_sizing: bool = False) -> None:
        """
        This function sets the sizing method.

        Parameters
        ----------
        L2_sizing : bool
            True if a sizing with the L2 method is needed
        L3_sizing : bool
            True if a sizing with the L3 method is needed
        L4_sizing : bool
            True if a sizing with the L4 method is needed

        Returns
        -------
        None
        """

        if not (L2_sizing or L3_sizing or L4_sizing):
            Warning("No sizing method is set to true, so nothing has changed.")

        # save sizing
        if L2_sizing:
            self._L2_sizing = L2_sizing
            self._L3_sizing = False
            self._L4_sizing = False
        if L3_sizing:
            self._L3_sizing = L3_sizing
            self._L2_sizing = False
            self._L4_sizing = False
        if L4_sizing:
            self._L4_sizing = L4_sizing
            self._L2_sizing = False
            self._L3_sizing = False

    @property
    def L2_sizing(self) -> bool:
        return self._L2_sizing

    @L2_sizing.setter
    def L2_sizing(self, L2_sizing) -> None:
        self._set_sizing(L2_sizing=L2_sizing)

    @property
    def L3_sizing(self) -> bool:
        return self._L3_sizing

    @L3_sizing.setter
    def L3_sizing(self, L3_sizing) -> None:
        self._set_sizing(L3_sizing=L3_sizing)

    @property
    def L4_sizing(self) -> bool:
        return self._L4_sizing

    @L4_sizing.setter
    def L4_sizing(self, L4_sizing) -> None:
        self._set_sizing(L4_sizing=L4_sizing)

    def make_backup(self) -> None:
        """
        This function sets the backup variable of the class.
        This is done by making a copy of the current class.

        Returns
        -------
        None
        """
        self._backup = copy.copy(self)

    def restore_backup(self) -> None:
        """
        This function restores the class to a previous backup using the self.backup variable.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            A value error is raised when this function is called before a backup has been made
        """
        if self._backup is None:
            raise ValueError("No backup has been made.")

        kwargs = {}
        for var in vars(self):
            kwargs[var] = self._backup.__getattribute__(var)
        self._set_sizing_setup(kwargs)
