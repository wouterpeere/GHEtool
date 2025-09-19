from ._Efficiency import _EfficiencyBase


class SEER(_EfficiencyBase):
    """
    Class for constant SEER efficiency
    """

    def __init__(self, SEER: float):
        """

        Parameters
        ----------
        SEER : float
            Seasonal Energy Efficiency Ratio [-]
        """

        self._SEER = None
        self.SEER = SEER
        self._has_part_load: bool = False

    @property
    def SEER(self) -> float:
        """
        This function returns the SEER.

        Returns
        -------
        SEER
            float
        """
        return self._SEER

    @SEER.setter
    def SEER(self, SEER) -> None:
        """
        This function sets the SEER.

        Parameters
        ----------
        SEER : float
            Seasonal Energy Efficiency Ratio [-]

        Raises
        ------
        ValueError
            When SEER < 1

        Returns
        -------
        None
        """
        if SEER < 1:
            raise ValueError(f'A value of {SEER} for the SEER is invalid.')
        self._SEER = SEER

    def get_SEER(self, *args, **kwargs) -> float:
        """
        This function returns the SEER.

        Returns
        -------
        SEER
            float
        """
        return self.SEER

    def get_EER(self, *args, **kwargs) -> float:
        """
        This function returns the EER.

        Returns
        -------
        EER
            float
        """
        return self.SEER

    def __export__(self):
        return {'SEER [-]': self.SEER}
