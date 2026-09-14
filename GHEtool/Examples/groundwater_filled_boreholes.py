from GHEtool import *
import numpy as np
import matplotlib.pyplot as plt
import pygfunction as gt


def graphs():
    fluid = TemperatureDependentFluidData('MEA', 25)

    flow = ConstantFlowRate(vfr=0.8)

    pipe_configurations = {
        'Single U-tube': {
            'groundwater': MultipleUTube(1.5, 0.013, 0.016, 0.4, 0.035, number_of_pipes=1, groundwater_filled=True
                                         ),
            'grout': MultipleUTube(1.3, 0.013, 0.016, 0.4, 0.035, number_of_pipes=1)
        },
        'Double U-tube': {
            'groundwater': MultipleUTube(1.5, 0.013, 0.016, 0.4, 0.035, number_of_pipes=2, groundwater_filled=True),
            'grout': MultipleUTube(1.3, 0.013, 0.016, 0.4, 0.035, number_of_pipes=2)
        }
    }

    q_array = np.arange(-50, 50, 1)

    H = 100

    r_b_array = [0.11 / 2, 0.15 / 2]
    T_b_array = [10, 5]
    kg_array = [1, 1.5, 2]

    Rb = {}
    Rb_grout = {}

    for configuration_name, pipes in pipe_configurations.items():

        groundwater_pipe = pipes['groundwater']
        grout_pipe = pipes['grout']

        for r_b in r_b_array:

            borehole = gt.boreholes.Borehole(H=H, D=0, r_b=r_b, x=0, y=0)

            groundwater_pipe.D_s = r_b / 2
            grout_pipe.D_s = r_b / 2

            for kg in kg_array:
                Rb_grout[(configuration_name, r_b, kg)] = []

            for T_b in T_b_array:

                Rb[(configuration_name, r_b, T_b)] = []

                for q in q_array:

                    T_start = T_b - 5

                    temp_rb = groundwater_pipe.explicit_model_borehole_resistance(fluid, flow, 2, borehole,
                                                                                  temperature_borehole_wall=T_b,
                                                                                  power=q / 1000 * H, nb_of_boreholes=1,
                                                                                  temperature=T_start)

                    T_fluid = T_b + q * temp_rb
                    temp_rb_prev = temp_rb

                    temp_rb = groundwater_pipe.explicit_model_borehole_resistance(fluid, flow, 2, borehole,
                                                                                  temperature_borehole_wall=T_b,
                                                                                  power=q / 1000 * H, nb_of_boreholes=1,
                                                                                  temperature=T_fluid)

                    while abs(temp_rb - temp_rb_prev) > 0.01:
                        T_fluid = T_b + q * temp_rb
                        temp_rb_prev = temp_rb

                        temp_rb = groundwater_pipe.explicit_model_borehole_resistance(fluid, flow, 2, borehole,
                                                                                      temperature_borehole_wall=T_b,
                                                                                      power=q / 1000 * H,
                                                                                      nb_of_boreholes=1,
                                                                                      temperature=T_fluid)
                    Rb[(configuration_name, r_b, T_b)].append(temp_rb)

                    if T_b == T_b_array[0]:

                        for kg in kg_array:
                            grout_pipe.k_g = kg

                            Rb_grout[(configuration_name, r_b, kg)].append(
                                grout_pipe.explicit_model_borehole_resistance(fluid, flow, 2, borehole,
                                                                              power=q / 1000 * H, nb_of_boreholes=1,
                                                                              temperature=T_fluid))

    # Create one graph for every borehole diameter and U-tube configuration
    for configuration_name in pipe_configurations:

        for r_b in r_b_array:

            borehole_diameter_mm = r_b * 2000

            plt.figure()

            for T_b in T_b_array:
                plt.plot(q_array, Rb[(configuration_name, r_b, T_b)], label=f'Tb: {T_b} °C, groundwater filled')

            for kg in kg_array:
                plt.plot(q_array, Rb_grout[(configuration_name, r_b, kg)], label=f'kg: {kg} W/(mK), grouted')

            plt.title(f'{configuration_name}, borehole diameter: '                f'{borehole_diameter_mm:.0f} mm')

            plt.ylabel('Effective borehole thermal resistance [mK/W]')
            plt.xlabel('Specific power [W/m]')

            plt.grid()
            plt.legend()
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    graphs()
