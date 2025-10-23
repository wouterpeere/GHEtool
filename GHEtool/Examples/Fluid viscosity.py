import pygfunction as gt
import matplotlib.pyplot as plt
import numpy as np
from GHEtool import *

temperature_array = np.arange(-10, 20, 1)
results_array = np.zeros((2, len(temperature_array)))

for idx, temp in enumerate(temperature_array):
    results_array[0][idx] = gt.media.Fluid('MPG', 20, temp).kinematic_viscosity()
    results_array[1][idx] = gt.media.Fluid('MPG', 30, temp).kinematic_viscosity()
    fluid = TemperatureDependentFluidData('MPG', 20)
    flow_rate = ConstantFlowRate(mfr=0.3)
    borehole = Borehole(fluid_data=fluid, flow_data=flow_rate,
                        pipe_data=DoubleUTube(1.8, 0.013, 0.016, 0.4, 0.35, 0.65))
    results_array[0][idx] = borehole.Re(temperature=temp)
    if temp < -7.2:
        results_array[0][idx] = np.nan
    fluid = TemperatureDependentFluidData('MPG', 30)
    borehole = Borehole(fluid_data=fluid, flow_data=flow_rate,
                        pipe_data=DoubleUTube(1.8, 0.013, 0.016, 0.4, 0.35, 0.65))
    results_array[1][idx] = borehole.Re(temperature=temp)
    
plt.figure()
plt.plot(temperature_array, results_array[0], label="MPG 20%")
plt.plot(temperature_array, results_array[1], label="MPG 30%")
plt.legend()
plt.xlabel('Temperature [°C]')
plt.ylabel('Reynolds number [-]')
plt.title('Reynolds number for different water-glycol mixtures')
plt.show()
