import abc
from abc import ABC


class _FlowRateData(ABC):

    @abc.abstractmethod
    def vfr(self, *args):
        """
        This function returns the volume flow rate [l/s].

        Parameters
        ----------
        args

        Returns
        -------

        """

    @abc.abstractmethod
    def mfr(self, *args):
        """
        This function returns the mass flow rate [kg/s].

        Parameters
        ----------
        args

        Returns
        -------

        """
