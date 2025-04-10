import abc
from abc import ABC


class _FlowData(ABC):

    @abc.abstractmethod
    def vfr(self, **kwargs):
        """
        This function returns the volume flow rate [l/s].

        Parameters
        ----------
        kwargs

        Returns
        -------

        """

    @abc.abstractmethod
    def mfr(self, **kwargs):
        """
        This function returns the mass flow rate [kg/s].

        Parameters
        ----------
        kwargs

        Returns
        -------

        """
