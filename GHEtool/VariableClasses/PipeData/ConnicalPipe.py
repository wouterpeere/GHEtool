import numpy as np
import pygfunction as gt

from math import pi

from GHEtool.VariableClasses.PipeData.SingleUTube import MultipleUTube
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class ConicalPipe(MultipleUTube):
    """
    This class contains the data for a conical pipe, where the wall thickness varies over the length of the pipe.

    More information on this technology and its advantages can be found here: https://www.hakagerodur.ch/de/gerotherm-vario/.
    """

    def __init__(self, k_g: float = None, r_in_start: float = None, r_in_stop: float = None,
                 begin_conical: float = None, end_conical: float = None, r_out: float = None,
                 k_p: float = None, D_s: float = None, number_of_pipes: int = None, epsilon: float = 1e-6):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/(mK)]
        r_in_start : float
            Inner pipe radius before the conical part [m]
        r_in_stop : float
            Inner pipe radius after the conical part [m]
        begin_conical : float
            Position at which the conical part starts [m]
        end_conical : float
            Position at which the conical part ends [m]
        r_out : float
            Outer pipe radius [m]
        k_p : float
            Pipe thermal conductivity [W/(mK)]
        D_s : float
            Distance of the pipe until center [m]
        number_of_pipes : int
            Number of pipes [#] (single U-tube: 1, double U-tube:2)
        epsilon : float
            Pipe roughness [m]
        """
        super().__init__(k_g=k_g, r_in=r_in_start, r_out=r_out, k_p=k_p, D_s=D_s, number_of_pipes=number_of_pipes,
                         epsilon=epsilon)

        self.r_in_start = r_in_start
        self.r_in_stop = r_in_stop
        self.begin_conical = begin_conical
        self.end_conical = end_conical

        # initiate pipes
        self._top_pipe = MultipleUTube(k_g, r_in_start, r_out, k_p, D_s, number_of_pipes, epsilon)
        self._end_pipe = MultipleUTube(k_g, r_in_stop, r_out, k_p, D_s, number_of_pipes, epsilon)

    def _get_pipe_model(self, y: float) -> tuple:
        """
        This function returns average pipe model at position y as well as the pipe model at the end.

        Parameters
        ----------
        y : float
            Depth at which the pipe model should be given.

        Returns
        -------
        Pipe Model: MultipleUTube
            Pipe model for the average inner diameter and Pipe model for the end inner diameter.

        Raises
        ------
        ValueError
            When y is not in the conical range.
        """
        if y < self.begin_conical or y > self.end_conical:
            raise ValueError(
                f'The value of {y} is not within the conical range of {self.begin_conical}m and {self.end_conical}m.')
        r_end = (self.r_in_stop - self.r_in_start) / (self.end_conical - self.begin_conical) * (
                y - self.begin_conical) + self.r_in_start
        r_avg = (r_end + self.r_in_start) / 2
        return MultipleUTube(self.k_g, r_avg, self.r_out, self.k_p, self.D_s, self.number_of_pipes, self.epsilon), \
            MultipleUTube(self.k_g, r_end, self.r_out, self.k_p, self.D_s, self.number_of_pipes, self.epsilon)

    def calculate_resistances(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                              **kwargs) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        None
        """
        self._top_pipe.calculate_resistances(fluid_data, flow_rate_data, **kwargs)

        if borehole_length <= self.begin_conical:
            self.R_f = self._top_pipe.R_f
            self.R_p = self._top_pipe.R_p
            return

        first_fraction = self.begin_conical / borehole_length

        if borehole_length <= self.end_conical:
            conical_part = self._get_pipe_model(borehole_length)[1]
            conical_part.calculate_resistances(fluid_data, flow_rate_data, **kwargs)
            conical_part_R_f_end = conical_part.R_f
            conical_part_R_p_end = conical_part.R_p
            conical_R_f_avg = (conical_part_R_f_end + self._top_pipe.R_f) / 2
            conical_R_p_avg = (conical_part_R_p_end + self._top_pipe.R_p) / 2

            self.R_f = self._top_pipe.R_f * first_fraction + conical_R_f_avg * (1 - first_fraction)
            self.R_p = self._top_pipe.R_p * first_fraction + conical_R_p_avg * (1 - first_fraction)
            return

        conical_fraction = (self.end_conical - self.begin_conical) / borehole_length

        conical_part = self._get_pipe_model(self.end_conical)[1]
        conical_part.calculate_resistances(fluid_data, flow_rate_data, **kwargs)

        conical_part_R_f_end = conical_part.R_f
        conical_part_R_p_end = conical_part.R_p
        conical_R_f_avg = (conical_part_R_f_end + self._top_pipe.R_f) / 2
        conical_R_p_avg = (conical_part_R_p_end + self._top_pipe.R_p) / 2

        self._end_pipe.calculate_resistances(fluid_data, flow_rate_data, **kwargs)

        self.R_f = self._top_pipe.R_f * first_fraction + \
                   conical_R_f_avg * conical_fraction + \
                   self._end_pipe.R_f * (1 - first_fraction - conical_fraction)
        self.R_p = self._top_pipe.R_p * first_fraction + \
                   conical_R_p_avg * conical_fraction + \
                   self._end_pipe.R_p * (1 - first_fraction - conical_fraction)

        return

    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float, **kwargs) -> float:
        """
        Average Reynolds number over the total borehole length.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        Reynolds number : float
        """
        first_part = self._top_pipe.Re(fluid_data, flow_rate_data, **kwargs)
        if borehole_length <= self.begin_conical:
            # only the first part
            return first_part

        first_fraction = self.begin_conical / borehole_length

        if borehole_length <= self.end_conical:
            conical_part = self._get_pipe_model(borehole_length)[0].Re(fluid_data, flow_rate_data, **kwargs)
            return first_part * first_fraction + \
                conical_part * (1 - first_fraction)

        conical_fraction = (self.end_conical - self.begin_conical) / borehole_length

        conical_part = self._get_pipe_model(self.end_conical)[0].Re(fluid_data, flow_rate_data, **kwargs)
        last_part = self._end_pipe.Re(fluid_data, flow_rate_data, **kwargs)

        return first_part * first_fraction + \
            conical_part * conical_fraction + \
            last_part * (1 - first_fraction - conical_fraction)

    def _pressure_conical(self, fluid_data, flow_rate_data, end, **kwargs) -> float:
        """
        Calculates the pressure drop of the conical part of the pipe.
        It takes an average of the friction factor between the beginning of the conical part and the friction factor
        at the end location. The average flow rate is calculated as the square of average of the quadratic flow rates.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        Pressure drop : float
            Pressure drop [kPa]
        """
        A = pi * self.r_in_start ** 2
        v_begin = (flow_rate_data.vfr(fluid_data=fluid_data, **kwargs) / 1000) / A / self.number_of_pipes
        f_begin = gt.pipes.fluid_friction_factor_circular_pipe(
            flow_rate_data.mfr(fluid_data=fluid_data, **kwargs) / self.number_of_pipes,
            self.r_in_start,
            fluid_data.mu(**kwargs),
            fluid_data.rho(**kwargs),
            self.epsilon)

        _, pipe_end = self._get_pipe_model(end)
        A = pi * pipe_end.r_in ** 2
        v_end = (flow_rate_data.vfr(fluid_data=fluid_data, **kwargs) / 1000) / A / self.number_of_pipes
        f_end = gt.pipes.fluid_friction_factor_circular_pipe(
            flow_rate_data.mfr(fluid_data=fluid_data, **kwargs) / self.number_of_pipes,
            pipe_end.r_in,
            fluid_data.mu(**kwargs),
            fluid_data.rho(**kwargs),
            self.epsilon)

        v_avg_quadratic = (v_begin ** 2 + v_end ** 2) / 2
        f_avg = (f_begin + f_end) / 2
        r_in_avg = (self.r_in_start + pipe_end.r_in) / 2
        return ((f_avg * (end - self.begin_conical) / (2 * r_in_avg)) * fluid_data.rho(
            **kwargs) * v_avg_quadratic ** 2 / 2) / 1000

    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        Pressure drop : float
            Pressure drop [kPa]
        """

        if borehole_length <= self.begin_conical:
            # only the first part
            return self._top_pipe.pressure_drop(fluid_data, flow_rate_data, borehole_length, **kwargs)

        first_part = self._top_pipe.pressure_drop(fluid_data, flow_rate_data, self.begin_conical, include_bend=False,
                                                  **kwargs)

        if self.begin_conical < borehole_length < self.end_conical:
            _, pipe_end = self._get_pipe_model(borehole_length)
            conical_part = self._pressure_conical(fluid_data, flow_rate_data, borehole_length, **kwargs)
            pressure_bend = pipe_end.pressure_drop(fluid_data, flow_rate_data, 0, **kwargs)  # only bend
            return first_part + conical_part + pressure_bend

        _, pipe_end = self._get_pipe_model(self.end_conical)
        conical_part = self._pressure_conical(fluid_data, flow_rate_data, self.end_conical, **kwargs)

        last_part = self._end_pipe.pressure_drop(fluid_data, flow_rate_data, borehole_length - self.end_conical,
                                                 **kwargs)
        return first_part + conical_part + last_part

    def __export__(self):
        pass
