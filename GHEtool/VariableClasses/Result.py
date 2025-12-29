"""
This file implements a Result class for temperature profiles.
"""
import abc
import numpy as np
import warnings

from abc import ABC


class _Results(ABC):

    def __init__(self, borehole_wall_temp: np.ndarray = np.array([])):
        """
        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        """
        self._Tb = borehole_wall_temp
        self.hourly = None

    @property
    def Tb(self) -> np.ndarray:
        return self._Tb

    @abc.abstractmethod
    def peak_extraction(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @abc.abstractmethod
    def peak_injection(self) -> np.ndarray:
        """

        Returns
        -------

        """

    @property
    def min_temperature(self) -> float:
        """
        Minimum average fluid temperature.

        Returns
        -------
        Minimum average fluid temperature
            float
        """
        if len(self.peak_extraction) == 0:
            return None
        return np.min(self.peak_extraction)

    @property
    def max_temperature(self) -> float:
        """
        Maximum average fluid temperature.

        Returns
        -------
        Maximum average fluid temperature
            float
        """
        if len(self.peak_injection) == 0:
            return None
        return np.max(self.peak_injection)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        for key in self.__dict__:
            value1 = self.__dict__[key]
            value2 = other.__dict__[key]
            if not np.array_equal(value1, value2):
                return False
        return True


class ResultsMonthly(_Results):
    """
    Class which contains the temperatures of the fluid and borehole wall with a monthly resolution.
    """

    def __init__(self,
                 borehole_wall_temp: np.ndarray = np.array([]),
                 peak_extraction: np.ndarray = np.array([]),
                 peak_injection: np.ndarray = np.array([]),
                 monthly_extraction: np.ndarray = np.array([]),
                 monthly_injection: np.ndarray = np.array([]),
                 baseload_temp: np.ndarray = np.array([])):
        """

        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        peak_extraction : np.ndarray
            Average fluid temperature in peak extraction [deg C]
        peak_injection : np.ndarray
            Average fluid temperature in peak injection [deg C]
        monthly_extraction : np.ndarray
            Average temperature due to average monthly extraction [deg C]
        monthly_injection : np.ndarray
            Average temperature due to average monthly injection [deg C]
        baseload_temp : np.ndarray
            Average fluid temperature due to the baseload [deg C]
        """
        self._peak_extraction = peak_extraction
        self._peak_injection = peak_injection
        self._monthly_extraction = monthly_extraction
        self._monthly_injection = monthly_injection
        self._baseload_temp = baseload_temp
        self._peak_extraction_inlet = np.array([])
        self._peak_extraction_outlet = np.array([])
        self._peak_injection_inlet = np.array([])
        self._peak_injection_outlet = np.array([])
        self._baseload_temp_inlet = np.array([])
        self._baseload_temp_outlet = np.array([])

        super().__init__(borehole_wall_temp)
        self.hourly = False

    @property
    def peak_extraction(self) -> np.ndarray:
        return self._peak_extraction

    @property
    def peak_injection(self) -> np.ndarray:
        return self._peak_injection

    @property
    def monthly_extraction(self) -> np.ndarray:
        warnings.warn("This will be removed in version 2.5.0. Please use 'baseload_temperature' instead.",
                      DeprecationWarning)
        return self._monthly_extraction

    @property
    def monthly_injection(self) -> np.ndarray:
        warnings.warn("This will be removed in version 2.5.0. Please use 'baseload_temperature' instead.",
                      DeprecationWarning)
        return self._monthly_injection

    @property
    def baseload_temperature(self) -> np.ndarray:
        return self._baseload_temp

    @property
    def baseload_temperature_inlet(self) -> np.ndarray:
        if not np.any(self._baseload_temp_inlet):
            raise ValueError('No inlet temperature for the baseload is set.')
        return self._baseload_temp_inlet

    @property
    def baseload_temperature_outlet(self) -> np.ndarray:
        if not np.any(self._baseload_temp_outlet):
            raise ValueError('No outlet temperature for the baseload is set.')
        return self._baseload_temp_outlet

    @property
    def baseload_temperature_delta(self) -> np.ndarray:
        """
        Temperature difference between inlet and outlet defined as temp_outlet - temp_inlet.

        Returns
        -------
        Temperature delta between the inlet and outlet fluid temperatures during baseload [°C]
        """
        return self.baseload_temperature_outlet - self.baseload_temperature_inlet

    @property
    def peak_injection_inlet(self) -> np.ndarray:
        if not np.any(self._peak_injection_inlet):
            raise ValueError('No inlet temperature for the peak injection is set.')
        return self._peak_injection_inlet

    @property
    def peak_injection_outlet(self) -> np.ndarray:
        if not np.any(self._peak_injection_outlet):
            raise ValueError('No outlet temperature for the peak injection is set.')
        return self._peak_injection_outlet

    @property
    def peak_injection_delta(self) -> np.ndarray:
        """
        Temperature difference between inlet and outlet defined as temp_outlet - temp_inlet.

        Returns
        -------
        Temperature delta between the inlet and outlet fluid temperatures during peak injection [°C]
        """
        return self.peak_injection_outlet - self.peak_injection_inlet

    @property
    def peak_extraction_inlet(self) -> np.ndarray:
        if not np.any(self._peak_extraction_inlet):
            raise ValueError('No inlet temperature for the peak extraction is set.')
        return self._peak_extraction_inlet

    @property
    def peak_extraction_outlet(self) -> np.ndarray:
        if not np.any(self._peak_extraction_outlet):
            raise ValueError('No outlet temperature for the peak extraction is set.')
        return self._peak_extraction_outlet

    @property
    def peak_extraction_delta(self) -> np.ndarray:
        """
        Temperature difference between inlet and outlet defined as temp_outlet - temp_inlet.

        Returns
        -------
        Temperature delta between the inlet and outlet fluid temperatures during peak extraction [°C]
        """
        return self.peak_extraction_outlet - self.peak_extraction_inlet


class ResultsHourly(_Results):
    """
    Class which contains the temperatures of the fluid and borehole wall with an hourly resolution.
    """

    def __init__(self,
                 borehole_wall_temp: np.ndarray = np.array([]),
                 temperature_fluid: np.ndarray = np.array([])):
        """

        Parameters
        ----------
        borehole_wall_temp : np.ndarray
            Borehole wall temperature [deg C]
        temperature_fluid : np.ndarray
            Average fluid temperature [deg C]
        """
        self._Tf = temperature_fluid

        self._Tf_extraction = None
        self._Tf_inlet = np.array([])
        self._Tf_outlet = np.array([])
        self._Tf_extraction_inlet = np.array([])
        self._Tf_extraction_outlet = np.array([])

        super().__init__(borehole_wall_temp)
        self.hourly = True

    @property
    def Tf(self) -> np.ndarray:
        return self._Tf

    @property
    def peak_extraction(self) -> np.ndarray:
        if self._Tf_extraction is not None:
            return self._Tf_extraction
        return self.Tf

    @property
    def peak_injection(self) -> np.ndarray:
        return self.Tf

    @property
    def peak_injection_inlet(self) -> np.ndarray:
        if not np.any(self._Tf_extraction_inlet):
            raise ValueError('No inlet temperature is set.')
        return self._Tf_inlet

    @property
    def peak_injection_outlet(self) -> np.ndarray:
        if not np.any(self._Tf_outlet):
            raise ValueError('No outlet temperature is set.')
        return self._Tf_outlet

    @property
    def peak_extraction_inlet(self) -> np.ndarray:
        if not np.any(self._Tf_extraction_inlet):
            return self.peak_injection_inlet
        return self._Tf_extraction_inlet

    @property
    def peak_extraction_outlet(self) -> np.ndarray:
        if not np.any(self._Tf_extraction_outlet):
            return self.peak_injection_outlet
        return self._Tf_extraction_outlet

    @property
    def peak_extraction_delta(self) -> np.ndarray:
        """
        Temperature difference between inlet and outlet defined as temp_outlet - temp_inlet.

        Returns
        -------
        Temperature delta between the inlet and outlet fluid temperatures during peak extraction [°C]
        """
        return self.peak_extraction_outlet - self.peak_extraction_inlet

    @property
    def peak_injection_delta(self) -> np.ndarray:
        """
        Temperature difference between inlet and outlet defined as temp_outlet - temp_inlet.

        Returns
        -------
        Temperature delta between the inlet and outlet fluid temperatures during peak injection [°C]
        """
        # identical
        return self.peak_injection_outlet - self.peak_injection_inlet

    @property
    def Tf_inlet(self) -> np.ndarray:
        return self.peak_injection_inlet

    @property
    def Tf_outlet(self) -> np.ndarray:
        return self.peak_injection_outlet

    @property
    def Tf_delta(self) -> np.ndarray:
        """
        Temperature difference between inlet and outlet defined as temp_outlet - temp_inlet.

        Returns
        -------
        Temperature delta between the inlet and outlet fluid temperatures during peak injection [°C]
        """
        # identical
        return self.peak_injection_outlet - self.peak_injection_inlet
