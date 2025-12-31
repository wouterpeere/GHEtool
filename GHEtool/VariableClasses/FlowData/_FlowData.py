import abc
from abc import ABC
from GHEtool.VariableClasses.BaseClass import BaseClass


class _FlowData(ABC, BaseClass):

    @abc.abstractmethod
    def vfr_borefield(self, **kwargs):
        """
        This function returns the volume flow rate for the entire borefield [l/s].

        Parameters
        ----------
        kwargs

        Returns
        -------

        """

    @abc.abstractmethod
    def mfr_borefield(self, **kwargs):
        """
        This function returns the mass flow rate for the entire borefield [kg/s].

        Parameters
        ----------
        kwargs

        Returns
        -------

        """

    @abc.abstractmethod
    def vfr_borehole(self, **kwargs):
        """
        This function returns the volume flow rate for a single borehole [l/s].

        Parameters
        ----------
        kwargs

        Returns
        -------

        """

    @abc.abstractmethod
    def mfr_borehole(self, **kwargs):
        """
        This function returns the mass flow rate for a single borehole [kg/s].

        Parameters
        ----------
        kwargs

        Returns
        -------

        """
