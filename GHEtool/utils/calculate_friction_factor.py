import numpy as np
from GHEtool.VariableClasses.FluidData._FluidData import _FluidData
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
    print(Re, fDarcy)
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

    pr = fluid.Pr(**kwargs)
    return (f / 8) * (Re - 1000) * pr / (1 + 12.7 * (f / 8) ** 0.5 * (pr ** (2 / 3) - 1))
