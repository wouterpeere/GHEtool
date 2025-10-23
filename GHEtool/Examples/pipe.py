import pygfunction as gt
from GHEtool import *

# pipe = gt.pipes.MultipleUTube(self.pos, 0.013, 0.016, borehole, k_s, self.k_g,
#                               self.R_p + self.R_f, self.number_of_pipes, J=2)

mfr = 0.65 * 1034 / 1000  # kg/s
Cp = 3855
temp = mfr * Cp  # W/K

lam = temp * 0.056 / 3.75
turb = temp * 0.16 / 3.22
print(lam, turb)

print(gt.media.Fluid('MPG', 25, -5))

pipe = MultipleUTube(1.5, 0.045 / 2 - 0.0015, 0.045 / 2, 0.4, 0.04, 1)
fluid = FluidData(mfr, 0.417, 1034, 3855, 8.12 * 0.001)
borehole = Borehole(fluid, pipe)
print('pyg', borehole.calculate_Rb(100, 1, 0.07, 2))
borehole.pipe_data.R_f = 1 / lam
print(borehole.Re)
print('smooth', borehole.calculate_Rb(100, 1, 0.07, 2))

borehole.pipe_data.R_f = 1 / turb
print('turbo', borehole.calculate_Rb(100, 1, 0.07, 2))
