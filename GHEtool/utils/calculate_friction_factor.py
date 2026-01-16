import numpy as np
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.FlowData._FlowData import _FlowData
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from typing import Union


def friction_factor_Haaland(Re: Union[float, np.ndarray], r_in: float, epsilon: float, **kwargs) -> Union[
    float, np.ndarray]:
    """
    Compute Darcy friction factor for an array of Reynolds numbers.

    Regimes
    Re < 2300      Laminar flow, f = 64 / Re
    Re > 4000      Turbulent flow, Haaland equation [#Haaland]_
    2300 <= Re <= 4000  Linear interpolation between both regimes

    Parameters
    ----------
    r_in : float
        Inner pipe radius [m]
    epsilon : float
        Pipe roughness [m]
    Re : np.array or float
        Reynolds numbers

    Returns
    -------
    f : ndarray
        Darcy friction factor(s)

    References
    ----------
    .. [#Haaland] Haaland, SE (1983). "Simple and Explicit Formulas for the Friction Factor in Turbulent Flow". Journal of Fluids Engineering. 105 (1): 89–90.
    """
    Re = np.asarray(Re, dtype=np.float64)

    f = np.empty_like(Re)

    # Laminar
    laminar = Re < 2300.0
    f[laminar] = 64.0 / Re[laminar]

    # Turbulent Haaland, smooth pipe
    turbulent = Re > 4000.0

    # Relative roughness
    E = epsilon / (r_in * 2)

    f[turbulent] = (1.0 / (-1.8 * np.log10((E / 3.7) ** 1.11 + 6.9 / Re[turbulent])) ** 2)

    # Transitional interpolation
    transitional = (~laminar) & (~turbulent)

    if np.any(transitional):
        f_2300 = 64.0 / 2300.0
        f_4000 = 1.0 / (-1.8 * np.log10(6.9 / 4000.0)) ** 2

        Re_t = Re[transitional]
        f[transitional] = (f_2300 + (Re_t - 2300.0) * (f_4000 - f_2300) / (4000.0 - 2300.0))

    return f


def friction_factor_darcy_weisbach(Re: Union[float, np.ndarray], r_in: float, epsilon: float, tol=1.0e-6, max_iter=100,
                                   **kwargs) -> Union[float, np.ndarray]:
    """
    Vectorized Darcy-Weisbach friction factor for circular pipes.

    Parameters
    ----------
    Re : np.array or float
        Reynolds numbers
    r_in : float
        Inner pipe radius [m]
    epsilon : float
        Pipe roughness [m]
    tol : float
        Relative convergence tolerance
    max_iter : int
        Maximum Colebrook iterations

    Returns
    -------
    f : ndarray
        Darcy friction factor(s)
    """
    Re = np.asarray(Re, dtype=np.float64)

    # Relative roughness
    E = epsilon / (r_in * 2)

    # Initialize friction factor array
    fDarcy = np.zeros_like(Re)

    # Laminar flow
    laminar = Re < 2.3e3
    fDarcy[laminar] = 64.0 / Re[laminar]

    # Turbulent flow
    turbulent = ~laminar
    if np.any(turbulent):
        f = np.full(np.sum(turbulent), 0.02)

        Re_t = Re[turbulent]

        for _ in range(max_iter):
            one_over_sqrt_f = -2.0 * np.log10(
                E / 3.7 + 2.51 / (Re_t * np.sqrt(f))
            )
            f_new = 1.0 / one_over_sqrt_f ** 2

            if np.all(np.abs((f_new - f) / f) < tol):
                break

            f = f_new

        fDarcy[turbulent] = f
    return fDarcy


def turbulent_nusselt(fluid: _FluidData, Re: Union[float, np.ndarray], f: Union[float, np.ndarray], **kwargs) -> Union[
    float, np.ndarray]:
    """
    Turbulent Nusselt number for smooth pipes based on (Gnielinski, 1976) [#Gnielinski]_.

    Parameters
    ----------
    fluid : _FluidData
        Fluid data object
    Re : np.array or float
        Reynolds numbers
    f : np.ndarray or float
        Friction factor [-]

    Returns
    -------
    float or np.ndarray
        Turbulent Nusselt numbers

    References
    ----------
    .. [#Gnielinski] Gnielinski, V. 1976. 'New equations for heat and mass transfer in turbulent pipe and channel flow.'
    International Chemical Engineering 16(1976), pp. 359-368.

    """
    pr = np.atleast_1d(np.asarray(fluid.Pr(**kwargs)))
    if 'array' in kwargs and len(pr) != 1:
        # this puts a mask on what values to calculate to save time
        pr = pr[kwargs.get('array')]
    return np.asarray((f / 8) * (Re - 1000) * pr / (1 + 12.7 * (f / 8) ** 0.5 * (pr ** (2 / 3) - 1)))


def calculate_convective_resistance(flow_data: _FlowData, fluid_data: _FluidData, r_in: float, nb_of_pipes: int,
                                    epsilon: float, **kwargs):
    """
    This function calculates the convective resistance.
    For the laminar flow, a fixed Nusselt number of 3.66 is used, for the turbulent flow, the Gnielinski
    equation is used. Linear interpolation is used over the range 2300 < Re < 4000 for the evaluation of the Nusselt number,
    as proposed by Gnielinski (2013) [#Gnielinksi2013]_.

    Parameters
    ----------
    flow_data : _FlowData
        Flow data object
    fluid_data : _FluidData
        Fluid data object
    r_in : float
        Inner pipe radius [m]
    nb_of_pipes : int
        Number of pipes [-]
    epsilon : float
        Pipe roughness [m]

    Returns
    -------
    float or np.ndarray
        Convective resistances

    References
    ----------
    .. [#Gnielinksi2013] Gnielinski, V. (2013). On heat transfer in tubes.
        International Journal of Heat and Mass Transfer, 63, 134–140.
        https://doi.org/10.1016/j.ijheatmasstransfer.2013.04.015
    """
    low_re = 2300.0
    high_re = 4000.0

    m_dot = np.atleast_1d(np.asarray(flow_data.mfr_borehole(**kwargs, fluid_data=fluid_data), dtype=np.float64))

    # Reynolds number
    re = 4.0 * m_dot / (fluid_data.mu(**kwargs) * np.pi * r_in * 2) / nb_of_pipes

    # Allocate Nusselt array
    nu = np.empty_like(re)

    # Laminar
    laminar = re < low_re
    nu[laminar] = 3.66

    # Turbulent
    turbulent = re > high_re
    if np.any(turbulent):
        if kwargs.get('haaland', False):
            f = friction_factor_Haaland(re[turbulent], r_in, epsilon, **kwargs)
        else:
            f = friction_factor_darcy_weisbach(re[turbulent], r_in, epsilon, **kwargs)
        nu[turbulent] = turbulent_nusselt(fluid_data, re[turbulent], f, array=turbulent, **kwargs)

    # Transitional interpolation
    transitional = (~laminar) & (~turbulent)

    if np.any(transitional):
        nu_low = 3.66
        if kwargs.get('haaland', False):
            # no array here to get a better fit with pygfunction (see validation file)
            f = friction_factor_Haaland(high_re, r_in, epsilon, **kwargs)
        else:
            f = friction_factor_darcy_weisbach(re[transitional], r_in, epsilon, **kwargs)
        nu_high = turbulent_nusselt(fluid_data, high_re, f, array=transitional, **kwargs)

        re_t = re[transitional]
        nu[transitional] = (nu_low + (re_t - low_re) * (nu_high - nu_low) / (high_re - low_re))

    # Convective resistance
    R_conv = 1.0 / (nu * np.pi * fluid_data.k_f(**kwargs))
    if R_conv.size == 1:
        return R_conv.item()
    return R_conv
