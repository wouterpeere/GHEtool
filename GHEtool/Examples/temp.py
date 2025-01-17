# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

import pygfunction as gt


def main():
    # -------------------------------------------------------------------------
    # Simulation parameters
    # -------------------------------------------------------------------------

    # Borehole dimensions
    D = .8  # Borehole buried length (m)
    H = 25  # Borehole length (m)
    r_b = 0.6  # Borehole radius (m)
    B = 2.0  # Borehole spacing (m)

    # Field of 10x7 (n=70) boreholes
    N_1 = 10
    N_2 = 7
    field = gt.boreholes.rectangle_field(N_1, N_2, B, B, H, D, r_b)

    # Thermal properties
    alpha = 2e-7  # Ground thermal diffusivity (m2/s)

    options_noCorrection = {
        'cylindrical_correction': False,
        'linear_threshold': 24 * 3600.}
    options_withCorrection = {
        'cylindrical_correction': True,
        'linear_threshold': 0.}

    # Geometrically expanding time vector.
    ts = H ** 2 / (9. * alpha)  # Bore field characteristic time
    # dt = 3600.                  # Time step
    # tmax = ts * np.exp(5)       # Maximum time
    # Nt = 50                     # Number of time steps
    # time = gt.utilities.time_geometric(dt, tmax, Nt)
    time = gt.load_aggregation.ClaessonJaved(3600, 3600 * 8760 * 20).get_times_for_simulation()
    lntts = np.log(time / ts)

    # -------------------------------------------------------------------------
    # Evaluate g-functions
    # -------------------------------------------------------------------------
    gfunc_noCorrection = gt.gfunction.gFunction(
        field, alpha, time=time, options=options_noCorrection,
        method='equivalent')
    gfunc_withCorrection = gt.gfunction.gFunction(
        field, alpha, time=time, options=options_withCorrection,
        method='equivalent')

    # Draw g-function
    ax = gfunc_noCorrection.visualize_g_function().axes[0]
    ax.plot(lntts, gfunc_withCorrection.gFunc)
    ax.legend(['Linear threshold',
               'Cylindrical correction', ])
    ax.set_title(f'Field of {len(field)} boreholes')
    plt.tight_layout()

    # Draw difference

    # Configure figure and axes
    fig = gt.utilities._initialize_figure()
    ax = fig.add_subplot(111)
    # Axis labels
    ax.set_xlabel(r'ln(t/t_s)')
    ax.set_ylabel(r'difference')
    gt.utilities._format_axes(ax)
    # Plot difference
    ax.plot(lntts, gfunc_withCorrection.gFunc)
    ax.set_title('Difference between g-functions')
    # Adjust to plot window
    plt.tight_layout()
    plt.show()


# Main function
if __name__ == '__main__':
    main()
