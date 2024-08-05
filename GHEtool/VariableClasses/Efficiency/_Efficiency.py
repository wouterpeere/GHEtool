import abc
from abc import ABC


class _COP(ABC):
    """
    Baseclass of the heating efficiency.
    """

    @abc.abstractmethod
    def get_COP(self) -> float:
        """
        This function returns the COP.

        Returns
        -------
        COP
            float
        """

    @abc.abstractmethod
    def get_SCOP(self) -> float:
        """
        This function returns the SCOP.

        Returns
        -------
        SCOP
            float
        """


class _EER(ABC):
    """
    Baseclass of the cooling efficiency.
    """

    @abc.abstractmethod
    def get_EER(self) -> float:
        """
        This function returns the EER.

        Returns
        -------
        EER
            float
        """

    @abc.abstractmethod
    def get_SEER(self) -> float:
        """
        This function returns the SEER.

        Returns
        -------
        SEER
            float
        """
