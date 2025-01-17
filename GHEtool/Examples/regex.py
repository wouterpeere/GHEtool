import pygfunction as gt

per = 10


# for per in range(1, 60):
#     mpg = gt.media.Fluid('MEG', per, 15)
#     water = gt.media.Fluid('Water', 0, 15)
#
#     total_mass = mpg.rho
#     mass_mpg = (total_mass - water.rho * (100 - per) / 100) / per * 100
#
#     print(f'{per}%: {mass_mpg}')


def convert_mass_per_to_vol_per(per):
    antifrost = gt.media.Fluid('MEG', per, 15)
    water = gt.media.Fluid('Water', 0, 15)
    total_mass = antifrost.rho
    mass_density_antifrost = (total_mass - water.rho * (100 - per) / 100) / per * 100

    return per * mass_density_antifrost / (999.0996087908144 * (100 - per) + mass_density_antifrost * per) * 100
