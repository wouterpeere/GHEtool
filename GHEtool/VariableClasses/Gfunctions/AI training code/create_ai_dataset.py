import pathlib
import threading
from time import process_time_ns, time_ns

import numpy as np
import pandas as pd
import pygfunction as gt

from GHEtool.VariableClasses.Gfunctions.CustomGFunction import _time_values

options: dict = {"method": "equivalent", "cylindrical_correction": True}
time_values = _time_values()


def save_dataframe(df: pd.DataFrame, file_path: str) -> None:
    """
    function to save dataframe

    Parameters
    ----------
    df: pd.DataFrame
    file_path: str

    Returns
    -------
        None
    """
    try:
        df.to_feather(file_path)
    except PermissionError:
        print(f"Error: File {file_path} is still open by another process/thread.")


def calc_f_gunc(vals: tuple[int, int, float, float, float, float, float, float, int]) -> list:
    """
    function to calculate g-function

    Parameters
    ----------
    vals: list
        list of variables for gfunction calcualtion

    Returns
    -------
        original list extended by results
    """
    N_1, N_2, B_1, B_2, H, D, r_b, alpha, shape = vals
    N_1, N_2 = int(N_1), int(N_2)
    if shape < 1:
        borefield = gt.borefield.Borefield.L_shaped_field(N_1, N_2, B_1, B_2, H, D, r_b)
    elif shape < 2:
        borefield = gt.borefield.Borefield.U_shaped_field(N_1, N_2, B_1, B_2, H, D, r_b)
    elif shape < 3:
        borefield = gt.borefield.Borefield.box_shaped_field(N_1, N_2, B_1, B_2, H, D, r_b)
    elif shape < 4:
        borefield = gt.borefield.Borefield.rectangle_field(N_1, N_2, B_1, B_2, H, D, r_b)
    else:
        borefield = gt.borefield.Borefield.staggered_rectangle_field(N_1, N_2, B_1, B_2, H, D, r_b, False)

    dt1 = process_time_ns()
    gfunc_calculated = gt.gfunction.gFunction(borefield, alpha, time_values, options=options,
                                              method=options["method"]).gFunc
    dt = (process_time_ns() - dt1) / 1000_000_000
    res_i = [N_1, N_2, B_1, B_2, H, D, r_b, alpha, shape, dt] + list(gfunc_calculated)
    return res_i


def main():
    # define column names
    columns = ["N_1", "N_2", "B_1", "B_2", "H", "D", "r_b", "alpha", "shape", "dt"] + [f"result_{i}" for i in
                                                                                       range(len(time_values))]
    # start list
    values = []
    # create sets of variables
    numbers = list(range(1, 4, 1)) + list(range(4, 10, 3)) + list(range(10, 31, 10))
    spacing = [2, 4, 6, 8, 10]
    depth = list(range(50, 200, 50)) + list(range(200, 500, 100))
    alpha = np.array([0.25, 0.4, 0.625, 0.8, 0.9, 1, 1.125, 1.75, 2.25, 2.67]) / 1000
    radii = list(np.arange(0.05, 0.15, 0.025).round(2)) + [0.15]
    shapes = range(5)
    burials = [0, 0.2, 0.5, 1, 2, 4]
    # create data list
    for shape in shapes:
        for N_1 in reversed(numbers):
            for N_2 in reversed(numbers):
                for B_1 in spacing:
                    for B_2 in spacing:
                        for H in depth:
                            for D in burials:
                                for alp in alpha:
                                    for r_b in radii:
                                        values.append((N_1, N_2, B_1, B_2, H, D, r_b, alp / 1000, shape))
    print(f"List ({len(values):_.0f}) created!")
    # read or create pandas dataframe
    if pathlib.Path("results_training_diff_fields.feather").exists():
        res = pd.read_feather("results_training_diff_fields.feather")
        start = res["N_1"].size
    else:
        res = pd.DataFrame(np.zeros((len(values), len(columns))), columns=columns, index=range(len(values)))
        print("pandas created!")
        start = 0
    # start calculation
    n_processes = 120
    tic = time_ns()
    for i in range(max(0, start - n_processes), len(values), n_processes):
        results = [calc_f_gunc(vals) for vals in values[slice(i, i + n_processes)]]
        res.iloc[slice(i, i + n_processes), :] = results
        print(f"calc time for {i}: {(time_ns() - tic) / 1_000_000_000:.0f} s")
        # Create a thread for saving the DataFrame
        save_thread = threading.Thread(target=save_dataframe, args=(res, "results_training_diff_fields.feather"))
        save_thread.start()


def short_term_corrections():
    times = gt.load_aggregation.ClaessonJaved(3600, 100 * 8760 * 3600).get_times_for_simulation()
    times = times[times < 3600 * 24]
    # create sets of variables
    depth = list(range(50, 200, 50)) + list(range(200, 500, 100))
    alpha = np.array([0.25, 0.4, 0.625, 0.8, 0.9, 1, 1.125, 1.75, 2.25, 2.67]) / 1000000
    radii = list(np.arange(0.05, 0.15, 0.025).round(2)) + [0.15]
    burials = [0, 0.2, 0.5, 1, 2, 4]
    g_store = np.zeros((len(depth), len(burials), len(alpha), len(radii), len(times)))

    # create data list
    for i, H in enumerate(depth):
        for j, D in enumerate(burials):
            for k, alp in enumerate(alpha):
                for l, r_b in enumerate(radii):
                    g = gt.gfunction.gFunction(
                        gt.boreholes.Borehole(H, D, r_b, 0, 0),
                        alp,
                        times
                    )
                    g_store[i, j, k, l, :] = g.gFunc
                    print(H, D, alp, r_b)
    np.save("g_store.npy", g_store)
    np.save("depth.npy", depth)
    np.save("burials.npy", burials)
    np.save("alpha.npy", alpha)
    np.save("radii.npy", radii)
    np.save("times.npy", times)


if __name__ == "__main__":
    main()
