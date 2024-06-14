import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


mod_Tconst250 = pd.read_csv("ModelicaResults/TavgFluid_250m_Tconst.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod250 = pd.read_csv("ModelicaResults/TavgFluid_250m.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod_Tconst200 = pd.read_csv("ModelicaResults/TavgFluid_200m_Tconst.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod200 = pd.read_csv("ModelicaResults/TavgFluid_200m.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod_Tconst150 = pd.read_csv("ModelicaResults/TavgFluid_150m_Tconst.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod150 = pd.read_csv("ModelicaResults/TavgFluid_150m.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod_Tconst107 = pd.read_csv("ModelicaResults/TavgFluid_L4_Tconst.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]
mod107 = pd.read_csv("ModelicaResults/TavgFluid_L4.csv", comment='#', sep=",", skiprows=[])["TAvgFluid"]

diff = np.array([np.average(mod_Tconst107[1:]-mod107[1:]),
                 np.average(mod_Tconst150[1:]-mod150[1:]),
                 np.average(mod_Tconst200[1:]-mod200[1:]),
                 np.average(mod_Tconst250[1:]-mod250[1:])])

plt.plot()
plt.plot(mod_Tconst107[1:]-mod107[1:], label="107m")
plt.plot(mod_Tconst150[1:]-mod150[1:], label="150m")
plt.plot(mod_Tconst200[1:]-mod200[1:], label="200m")
plt.plot(mod_Tconst250[1:]-mod250[1:], label="250m")
plt.xlabel("Time in seconds")
plt.ylabel("Difference in temperature")
plt.legend()


xrange = np.array([107, 150, 200, 250])

plt.figure()
plt.plot(xrange, diff)
plt.xlabel("Depth")
plt.ylabel("Difference in temperature")
plt.show()
