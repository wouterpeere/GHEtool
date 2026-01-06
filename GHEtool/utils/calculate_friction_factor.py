import numpy as np
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
from GHEtool.VariableClasses.PipeData._PipeData import _PipeData
from typing import Union


def friction_factor(Re: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Compute Darcy friction factor for an array of Reynolds numbers.

    Regimes
    Re < 2300      Laminar flow, f = 64 / Re
    Re > 4000      Turbulent flow, Haaland equation, smooth pipe [#Haaland]_
    2300 <= Re <= 4000  Linear interpolation between both regimes

    Parameters
    ----------
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
    # TODO adapt for non-smooth pipes
    f[turbulent] = (1.0 / (-1.8 * np.log10(6.9 / Re[turbulent])) ** 2)

    # Transitional interpolation
    transitional = (~laminar) & (~turbulent)

    if np.any(transitional):
        f_2300 = 64.0 / 2300.0
        f_4000 = 1.0 / (-1.8 * np.log10(6.9 / 4000.0)) ** 2

        Re_t = Re[transitional]
        f[transitional] = (f_2300 + (Re_t - 2300.0) * (f_4000 - f_2300) / (4000.0 - 2300.0))

    return f


def turbulent_nusselt(fluid: _FluidData, Re: Union[float, np.ndarray], **kwargs) -> Union[float, np.ndarray]:
    """
    Turbulent Nusselt number for smooth pipes based on (Gnielinski, 1976) [#Gnielinski]_.

    Parameters
    ----------
    fluid : _FluidData
        Fluid data object
    Re : np.array or float
        Reynolds numbers

    Returns
    -------
    float or np.ndarray
        Turbulent Nusselt numbers

    References
    ----------
    .. [#Gnielinski] Gnielinski, V. 1976. 'New equations for heat and mass transfer in turbulent pipe and channel flow.'
    International Chemical Engineering 16(1976), pp. 359-368.

    """

    f = friction_factor(Re)
    pr = fluid.Pr(**kwargs)
    return (f / 8) * (Re - 1000) * pr / (1 + 12.7 * (f / 8) ** 0.5 * (pr ** (2 / 3) - 1))
