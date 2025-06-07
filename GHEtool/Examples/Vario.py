from GHEtool import *
import matplotlib.pyplot as plt
import numpy as np

regular_pipe = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
regular_pipe_PN12 = SingleUTube(1.5, 0.0135, 0.016, 0.4, 0.035)
vario = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)

fluid = TemperatureDependentFluidData('MEG', 25).create_constant(3)
flow = ConstantFlowRate(vfr=0.9 / 3.6)

length = np.arange(100, 160, 1)

dp_regular = [regular_pipe.pressure_drop(fluid, flow, i) for i in length]
dp_vario = [vario.pressure_drop(fluid, flow, i) for i in length]

reynolds_regular = [regular_pipe.Re(fluid, flow, borehole_length=i) for i in length]
reynolds_vario = [vario.Re(fluid, flow, borehole_length=i) for i in length]

plt.figure()
plt.plot(length, dp_vario, label="vario")
plt.plot(length, dp_regular, label="regular")
plt.xlabel('Length [m]')
plt.ylabel('Pressure drop [kPa]')
plt.legend()

plt.figure()
plt.plot(length, reynolds_vario, label="vario")
plt.plot(length, reynolds_regular, label="regular")
plt.xlabel('Length [m]')
plt.ylabel('Reynolds [-]')
plt.legend()

# borehole resistance
vfr_range = np.arange(0.05, 0.8, 0.005)

rb_regular = []
rb_regular_pn12 = []
rb_vario = []
r_f_regular = []
r_p_regular = []
r_f_regular_pn12 = []
r_p_regular_pn12 = []
r_f_vario = []
r_p_vario = []
for vfr in vfr_range:
    flow = ConstantFlowRate(vfr=vfr)
    borehole_regular = Borehole(fluid, regular_pipe, flow)
    borehole_vario = Borehole(fluid, vario, flow)
    borehole_regular_pn12 = Borehole(fluid, regular_pipe_PN12, flow)
    rb_regular.append(borehole_regular.get_Rb(160, 1, 0.07, 2))
    rb_regular_pn12.append(borehole_regular_pn12.get_Rb(160, 1, 0.07, 2))

    rb_vario.append(borehole_vario.get_Rb(160, 1, 0.07, 2))
    r_f_regular.append(borehole_regular.pipe_data.R_f)
    r_f_regular_pn12.append(borehole_regular_pn12.pipe_data.R_f)
    r_p_regular.append(borehole_regular.pipe_data.R_p)
    r_p_regular_pn12.append(borehole_regular_pn12.pipe_data.R_p)
    r_f_vario.append(borehole_vario.pipe_data.R_f)
    r_p_vario.append(borehole_vario.pipe_data.R_p)

plt.figure()
plt.plot(vfr_range, rb_vario, label="vario")
plt.plot(vfr_range, rb_regular, label="regular PN 16")
plt.plot(vfr_range, rb_regular_pn12, label="regular PN12")

plt.xlabel('Volume flow rate [l/s]')
plt.ylabel('Effective borehole thermal resistance [W/(mK)]')
plt.legend()

plt.figure()
plt.plot(vfr_range, r_p_vario, label="R_p vario")
plt.plot(vfr_range, r_p_regular, label="R_p regular PN16")
plt.plot(vfr_range, r_p_regular_pn12, label="R_p regular PN12")
plt.plot(vfr_range, r_f_vario, label="R_f vario")
plt.plot(vfr_range, r_f_regular, label="R_f regular PN16")
plt.plot(vfr_range, r_f_regular_pn12, label="R_f regular PN12")
plt.xlabel('Volume flow rate [l/s]')
plt.ylabel('Effective borehole thermal resistance [W/(mK)]')
plt.legend()
plt.show()
