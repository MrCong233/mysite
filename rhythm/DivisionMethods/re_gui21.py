import os.path
import pandas as pd
import numpy as np
# from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

from . import equal_grid
from . import kdtree
from . import equal_3d
from . import kdtree_3
from . import hebing
from . import time_space
from . import space_time

# import equal_grid
# import kdtree
# import equal_3d
# import kdtree_3
# import hebing
# import time_space
# import space_time


def calc_ent(x):
    """calculating the information entropy
    """
    x_value_list = set([x[i] for i in range(x.shape[0])])
    ent = 0.0
    for x_value in x_value_list:
        p = float(x[x == x_value].shape[0]) / x.shape[0]
        logp = np.log2(p)
        ent -= p * logp
    return ent


def figure_to_img(dataset_, method_, args, test_or_not):
    """dataset_ is the full name of dataset in csv format file,
        method_ is the full name of selected method,
        args is an list of arguments.
        PS:
            The format of dataset_ is like "dataset1",
            and of method_ is one of the following: "2d_equal_grid",
            "2d_kdtree", "3d_equal_grid", "3d_kdtree", "3d_slice_merge",
            "time_space", "space_time", and of args is like [5] or [4, 10]
        Return image full name and extra information.
        PS:
            image full name is a string like "dataset_name-method-argument.png",
            extra information is a string list contains information as following order:
                information entropy,
                variance,
                standard deviation,
                arithmetic mean,
                minimum,
                maximum,
                skew,
                kurtosis,
                number.
    """
    # "\\..\\static\\rhythm\\img\\generated\\"
    dirname_ = os.path.dirname(os.path.abspath(__file__))
    # print("*", dirname_)
    dataset_path = dirname_ + "\\dataset\\" + dataset_
    database_ = np.array(pd.read_csv(dataset_path + ".csv", header=None))
    # print(database_)
    if test_or_not == False:
        img_path = dirname_ + "\\..\\static\\rhythm\\img\\generated\\"
    else:
        img_path = dirname_ + "\\generated\\" + method_
        # print(img_path)
    Path(img_path).mkdir(parents=True, exist_ok=True)
    img_address = img_path + "\\"
    img_name = dataset_ + "-"
    whole_figure = plt.figure()
    if method_ == "2d_equal_grid":
        parameter_ = args[0]
        subplot_added = whole_figure.add_subplot(1, 1, 1)
        equal_grid.equal_grid(subplot_added, database_, parameter_)
        grid_count = equal_grid.state_grid(database_, parameter_)
        img_name += method_ + "-" + str(parameter_)
    if method_ == "2d_kdtree":
        parameter_ = args[0]
        subplot_added = whole_figure.add_subplot(1, 1, 1)
        grid_count = kdtree.draw_fig(database_, subplot_added, parameter_)
        img_name += method_ + "-" + str(parameter_)
    if method_ == "3d_equal_grid":
        parameter_ = args[0]
        subplot_added = Axes3D(whole_figure)
        equal_3d.draw_fig(database_, subplot_added, parameter_)
        grid_count = equal_3d.state_num(database_, parameter_)
        img_name += method_ + "-" + str(parameter_)
    if method_ == "3d_kdtree":
        parameter_ = args[0]
        subplot_added = whole_figure.gca(projection='3d')
        grid_count = kdtree_3.draw_fig(database_, parameter_, subplot_added)
        img_name += method_ + "-" + str(parameter_)
    if method_ == "3d_slice_merge":
        hebing.xifen(database_, xs=10, ys=10, zs=10)  # slice
        hebing.hebing2(database_)                        # merge
        parameter_ = args[0]
        hebing.draw_fig(database_, parameter_, whole_figure)
        grid_count = hebing.state_num()
        img_name += method_ + "-" + str(parameter_)
    if method_ == "time_space":
        parameter_first = args[0]
        parameter_second = args[1]
        grid_count = time_space.draw_fig(database_, parameter_first,
                                         parameter_second, whole_figure)
        img_name += method_ + "-" + \
            str(parameter_first) + "-" + str(parameter_second)
    if method_ == "space_time":
        parameter_first = args[0]
        parameter_second = args[1]
        grid_count = space_time.draw_f7(database_, parameter_first,
                                        parameter_second, whole_figure)
        img_name += method_ + "-" + \
            str(parameter_first) + "-" + str(parameter_second)
    img_address += img_name + ".png"
    whole_figure.savefig(img_address)
    plt.close()
    # whole_figure.clf()
    # print(grid_count)
    if len(grid_count) != 0:
        extra_information = {
            "information_entropy": str(round(calc_ent(np.array(grid_count)), 2)),
            "varience": str(round(np.var(grid_count), 2)),
            "standard_deviation": str(round(np.std(grid_count), 2)),
            "mean": str(round(np.mean(grid_count), 2)),
            "min": str(round(np.min(grid_count), 2)),
            "max": str(round(np.max(grid_count), 2)),
            "skew": str(round(pd.Series(grid_count).skew(), 2)),
            "kurtosis": str(round(pd.Series(grid_count).kurt(), 2)),
            "len": str(round(len(grid_count), 2)),
        }
    else:
        extra_information = {}
        Path(img_address).unlink()
        img_address = ""
    return img_address, extra_information
