import matplotlib.pyplot as plt
from GHEtool import *
import numpy as np
import time

fluid = TemperatureDependentFluidData('MPG', 25)
pipe = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

Rb_ghe = []
Rb_explicit_0 = []
Rb_explicit_1 = []
Rb_explicit_1_alt = []
Rb_explicit_2 = []


def friction_factor(Re):
    """
    Compute Darcy friction factor for an array of Reynolds numbers.

    Regimes
    Re < 2300      Laminar flow, f = 64 / Re
    Re > 4000      Turbulent flow, Haaland equation, smooth pipe
    2300 <= Re <= 4000  Linear interpolation between both regimes

    Parameters
    ----------
    Re : array_like
        Reynolds numbers

    Returns
    -------
    f : ndarray
        Darcy friction factors
    """

    Re = np.asarray(Re, dtype=np.float64)

    f = np.empty_like(Re)

    # Laminar
    laminar = Re < 2300.0
    f[laminar] = 64.0 / Re[laminar]

    # Turbulent Haaland, smooth pipe
    turbulent = Re > 4000.0
    f[turbulent] = (
            1.0
            / (-1.8 * np.log10(6.9 / Re[turbulent])) ** 2
    )

    # Transitional interpolation
    transitional = (~laminar) & (~turbulent)

    if np.any(transitional):
        f_2300 = 64.0 / 2300.0
        f_4000 = 1.0 / (-1.8 * np.log10(6.9 / 4000.0)) ** 2

        Re_t = Re[transitional]
        f[transitional] = (
                f_2300
                + (Re_t - 2300.0)
                * (f_4000 - f_2300)
                / (4000.0 - 2300.0)
        )

    return f


def turbulent_nusselt(fluid: TemperatureDependentFluidData, re, temp):
    """
    Turbulent Nusselt number for smooth pipes

    Gnielinski, V. 1976. 'New equations for heat and mass transfer in turbulent pipe and channel flow.'
    International Chemical Engineering 16(1976), pp. 359-368.

    :param re: Reynolds number
    :param temp: temperature, C
    :return: Nusselt number
    """

    f = friction_factor(re)
    pr = fluid.Pr(temperature=temp)
    return (f / 8) * (re - 1000) * pr / (1 + 12.7 * (f / 8) ** 0.5 * (pr ** (2 / 3) - 1))


def calc_conv_resist(m_dot, temp, fluid: TemperatureDependentFluidData, inner_diam):
    low_re = 2300.0
    high_re = 4000.0

    m_dot = np.asarray(m_dot, dtype=np.float64)

    # Reynolds number
    re = 4.0 * m_dot / (fluid.mu(temperature=temp) * np.pi * inner_diam)

    # Allocate Nusselt array
    nu = np.empty_like(re)

    # Laminar
    laminar = re < low_re
    nu[laminar] = 3.66

    # Turbulent
    turbulent = re > high_re
    nu[turbulent] = turbulent_nusselt(fluid, re[turbulent], temp)

    # Transitional interpolation
    transitional = (~laminar) & (~turbulent)

    if np.any(transitional):
        nu_low = 3.66
        nu_high = turbulent_nusselt(fluid, high_re, temp)

        re_t = re[transitional]
        nu[transitional] = (
                nu_low
                + (re_t - low_re)
                * (nu_high - nu_low)
                / (high_re - low_re)
        )

    # Convective resistance
    return 1.0 / (nu * np.pi * fluid.k_f(temperature=temp))


def pipe_res(pipe: SingleUTube):
    return np.log(pipe.r_out / pipe.r_in) / (2 * np.pi * pipe.k_p)


# GHEtool
start = time.time()
for val in np.linspace(0.1, 2, 100):
    flow = ConstantFlowRate(mfr=val)
    borehole = Borehole(fluid, pipe, flow)
    borehole.use_constant_Rb = False
    Rb_ghe.append(borehole.get_Rb(100, 1, 0.075, 2, temperature=5))

print(f'GHEtool: {(time.time() - start)} ms')


def Ra(pipe: SingleUTube, Rp, order=0):
    beta = Rp * 2 * np.pi * pipe.k_g  # 1.5 is grout
    theta_1 = 2 * pipe.D_s / (0.075 * 2)
    theta_2 = 0.075 * 2 / (pipe.r_out * 2)
    theta_3 = 1 / (2 * theta_1 * theta_2)
    sigma = (pipe.k_g - 2) / (
            pipe.k_g + 2
    )
    term_1_num = (1 + theta_1 ** 2) ** sigma
    term_1_den = theta_3 * (1 - theta_1 ** 2) ** sigma
    final_term_1 = np.log(term_1_num / term_1_den)

    term_2_num = theta_3 ** 2 * (1 - theta_1 ** 4 + 4 * sigma * theta_1 ** 2) ** 2
    term_2_den_pt_1 = (1 + beta) / (1 - beta) * (1 - theta_1 ** 4) ** 2
    term_2_den_pt_2 = theta_3 ** 2 * (1 - theta_1 ** 4) ** 2
    term_2_den_pt_3 = 8 * sigma * theta_1 ** 2 * theta_3 ** 2 * (1 + theta_1 ** 4)
    term_2_den = term_2_den_pt_1 - term_2_den_pt_2 + term_2_den_pt_3
    final_term_2 = term_2_num / term_2_den
    return 1 / (np.pi * pipe.k_g) * (beta + final_term_1 - final_term_2)


def Rb(pipe: SingleUTube, Rp, order=0):
    beta = Rp * 2 * np.pi * pipe.k_g  # 1.5 is grout
    theta_1 = 2 * pipe.D_s / (0.075 * 2)
    theta_2 = 0.075 * 2 / (pipe.r_out * 2)
    theta_3 = 1 / (2 * theta_1 * theta_2)
    sigma = (pipe.k_g - 2) / (
            pipe.k_g + 2
    )
    final_term_1 = np.log(theta_2 / (2 * theta_1 * (1 - theta_1 ** 4) ** sigma))

    term_2_num = theta_3 ** 2 * (1 - (4 * sigma * theta_1 ** 4) / (1 - theta_1 ** 4)) ** 2
    term_2_den_pt_1 = (1 + beta) / (1 - beta)
    term_2_den_pt_2 = theta_3 ** 2 * (1 + (16 * sigma * theta_1 ** 4) / (1 - theta_1 ** 4) ** 2)
    term_2_den = term_2_den_pt_1 + term_2_den_pt_2
    final_term_2 = term_2_num / term_2_den

    return (1 / (4 * np.pi * pipe.k_g)) * (beta + final_term_1 - final_term_2)


start = time.time()
# explicit 0
for val in np.linspace(0.1, 2, 100):
    R_p = pipe_res(pipe) + calc_conv_resist(val / 2, 5, fluid, pipe.r_in * 2)
    sigma = (pipe.k_g - 2) / (
            pipe.k_g + 2
    )
    Rb_0 = R_p / 4 + 1 / (8 * np.pi * pipe.k_g) * (
            np.log(0.075 ** 4 / (4 * pipe.r_out * pipe.D_s ** 3)) + sigma * np.log(
        0.075 ** 8 / (0.075 ** 8 - pipe.D_s ** 8)))
    Ra_0 = 2 * R_p + 2 / (2 * np.pi * pipe.k_g) * (np.log(pipe.D_s / (pipe.r_out)) + sigma * np.log(
        (0.075 ** 4 + pipe.D_s ** 4) / (0.075 ** 4 - pipe.D_s ** 4)))
    r_a = Ra_0  # R_a
    r_b = Rb_0  # R_b
    r_v = 100 / (val / 2 * fluid.cp(temperature=5))  # (K/(w/m)) thermal resistance factor
    n = r_v / (r_b * r_a) ** 0.5
    Rb_explicit_0.append(r_b * n * np.cosh(n) / np.sinh(n))
print(f'Explicit 0: {(time.time() - start)} ms')
start = time.time()

# explicit 1
for val in np.linspace(0.1, 2, 100):
    R_p = pipe_res(pipe) + calc_conv_resist(val / 2, 5, fluid, pipe.r_in * 2)
    sigma = (pipe.k_g - 2) / (
            pipe.k_g + 2
    )
    beta = R_p * 2 * np.pi * pipe.k_g
    ppc = pipe.r_out ** 2 / (4 * pipe.D_s ** 2)
    pc = pipe.D_s ** 2 / ((0.075 ** 8 - pipe.D_s ** 8) ** (1 / 4))
    pb = 0.075 ** 2 / ((0.075 ** 8 - pipe.D_s ** 8) ** (1 / 4))
    b1 = (1 - beta) / (1 + beta)

    Rb_0 = R_p / 4 + 1 / (8 * np.pi * pipe.k_g) * (
            np.log(0.075 ** 4 / (4 * pipe.r_out * pipe.D_s ** 3)) + sigma * np.log(
        0.075 ** 8 / (0.075 ** 8 - pipe.D_s ** 8)))
    Ra_0 = 2 * R_p + 2 / (2 * np.pi * pipe.k_g) * (np.log(pipe.D_s / (pipe.r_out)) + sigma * np.log(
        (0.075 ** 4 + pipe.D_s ** 4) / (0.075 ** 4 - pipe.D_s ** 4)))
    Bb_1 = 1 / (8 * np.pi * pipe.k_g) * (b1 * ppc * (3 - 8 * sigma * pc ** 4) ** 2) / (
            1 + b1 * ppc * (5 + 64 * sigma * pc ** 4 * pb ** 4))
    Ba_1 = 2 / (2 * np.pi * pipe.k_g) * (b1 * ppc * (1 + 8 * sigma * pc ** 2 * pb ** 2) ** 2) / (
            1 - b1 * ppc * (3 - 32 * sigma * (pc ** 2 * pb ** 6 + pc ** 6 * pb ** 2)))

    r_a = Ra_0 - Ba_1  # R_a
    r_b = Rb_0 - Bb_1  # R_b
    r_v = 100 / (val / 2 * fluid.cp(temperature=5))  # (K/(w/m)) thermal resistance factor
    n = r_v / (r_b * r_a) ** 0.5
    Rb_explicit_1.append(r_b * n * np.cosh(n) / np.sinh(n))
print(f'Explicit 1: {(time.time() - start)} ms')
start = time.time()

# explicit 2
for val in np.linspace(0.1, 2, 100):
    R_p = pipe_res(pipe) + calc_conv_resist(val / 2, 5, fluid, pipe.r_in * 2)
    sigma = (pipe.k_g - 2) / (
            pipe.k_g + 2
    )
    beta = R_p * 2 * np.pi * pipe.k_g
    ppc = pipe.r_out ** 2 / (4 * pipe.D_s ** 2)
    pc = pipe.D_s ** 2 / ((0.075 ** 8 - pipe.D_s ** 8) ** (1 / 4))
    pb = 0.075 ** 2 / ((0.075 ** 8 - pipe.D_s ** 8) ** (1 / 4))
    b1 = (1 - beta) / (1 + beta)

    Rb_0 = R_p / 4 + 1 / (8 * np.pi * pipe.k_g) * (
            np.log(0.075 ** 4 / (4 * pipe.r_out * pipe.D_s ** 3)) + sigma * np.log(
        0.075 ** 8 / (0.075 ** 8 - pipe.D_s ** 8)))
    Ra_0 = R_p + 1 / (2 * np.pi * pipe.k_g) * (np.log(pipe.D_s / (pipe.r_out)) + sigma * np.log(
        (0.075 ** 4 + pipe.D_s ** 4) / (0.075 ** 4 - pipe.D_s ** 4)))
    Ba_1 = 1 / (8 * np.pi * pipe.k_g) * (b1 * ppc * (3 - 8 * sigma * pc ** 4) ** 2) / (
            1 + b1 * ppc * (5 + 64 * sigma * pc ** 4 * pb ** 4))
    Bb_1 = 2 / (2 * np.pi * pipe.k_g) * (b1 * ppc * (1 + 8 * sigma * pc ** 2 * pb ** 2) ** 2) / (
            1 - b1 * ppc * (3 - 32 * sigma * (pc ** 2 * pb ** 6 + pc ** 6 * pb ** 2)))

    r_a = Ra_0  # R_a
    r_b = Rb_0  # R_b
    r_v = 100 / (val / 2 * fluid.cp(temperature=5))  # (K/(w/m)) thermal resistance factor
    n = r_v / (r_b * r_a) ** 0.5
    Rb_explicit_2.append(r_b * n * np.cosh(n) / np.sinh(n))

print(f'Explicit 2: {(time.time() - start)} ms')

plt.figure()
plt.plot(Rb_ghe, label="GHE")
plt.plot(Rb_explicit_0, label="Explicit 0")
plt.plot(Rb_explicit_1, label="Explicit 1")
# plt.plot(Rb_explicit_2, label="Explicit 2")

# plt.show()
plt.legend()
plt.figure()
plt.plot((np.array(Rb_ghe) - np.array(Rb_explicit_0)) * 100, label="Explicit 0")
plt.plot((np.array(Rb_ghe) - np.array(Rb_explicit_1)) * 100, label="Explicit 1")
# plt.plot((np.array(Rb_ghe) - np.array(Rb_explicit_2)) * 100, label="Explicit 2")

plt.legend()
plt.show()
