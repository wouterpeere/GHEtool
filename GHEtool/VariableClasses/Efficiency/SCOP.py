class SCOP:
    """
    Class for constant SCOP efficiency
    """

    def __init__(self, SCOP: float):
        """

        Parameters
        ----------
        SCOP : float
            Seasonal Coefficient Of Performance [-]
        """
        self._SCOP = None
        self.SCOP = SCOP
        self._range_part_load = False

    @property
    def SCOP(self) -> float:
        """
        This function returns the SCOP.

        Returns
        -------
        SCOP
            float
        """
        return self._SCOP

    @SCOP.setter
    def SCOP(self, SCOP) -> None:
        """
        This function sets the SCOP.

        Parameters
        ----------
        SCOP : float
            Seasonal Coefficient Of Performance [-]

        Raises
        ------
        ValueError
            When SCOP < 1

        Returns
        -------
        None
        """
        if SCOP < 1:
            raise ValueError(f'A value of {SCOP} for the SCOP is invalid.')
        self._SCOP = SCOP

    def get_SCOP(self, *args, **kwargs) -> float:
        """
        This function returns the SCOP.

        Returns
        -------
        SCOP
            float
        """
        return self.SCOP

    def get_COP(self, *args, **kwargs) -> float:
        """
        This function returns the COP.

        Returns
        -------
        COP
            float
        """
        return self.SCOP
