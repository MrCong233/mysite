# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 10:48:46 2018

@author: admin
"""

'''
等网格划分
'''
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.patches as patches


def equal_grid(ax, df, sp):
    '''
    二维等网格
    画图
    '''

    ax.scatter(df[:, 1], df[:, 2], s=1)
    ax.set_xlabel('longitude')
#     ax.set_xlabel('经度')
    ax.set_ylabel('latitude')
#     ax.set_ylabel('纬度')
    ax.set_title('2d_equal_grid')
    x_min = min(df[:, 1])
    x_max = max(df[:, 1])
    y_max = max(df[:, 2])
    y_min = min(df[:, 2])
    rec_len = (x_max - x_min)/sp
    rec_wid = (y_max - y_min)/sp
    ax.add_patch(patches.Rectangle((x_min, y_min),
                                   rec_len, rec_wid, ec='k', fc='none'))
    grid_loc = np.zeros((sp*sp, 2))
    grid_loc[0, 0] = x_min
    grid_loc[0, 1] = y_min
    for i in range(sp):
        y_min1 = y_min + i*rec_wid
        for j in range(sp):
            x_min1 = x_min + j*rec_len
            grid_loc[i*sp+j, 0] = x_min1
            grid_loc[i*sp+j, 1] = y_min1
            ax.add_patch(patches.Rectangle((x_min1, y_min1),
                                           rec_len, rec_wid, ec='k', fc='none'))


def state_grid(df, sp):
    '''
    统计每个网格内点的数量
    '''
    grid_num = []
    x_min = min(df[:, 1])
    x_max = max(df[:, 1])
    y_max = max(df[:, 2])
    y_min = min(df[:, 2])
    rec_len = (x_max - x_min)/sp
    rec_wid = (y_max - y_min)/sp
    for i in range(sp):
        x_min1 = x_min + rec_len*i
        for j in range(sp):
            y_min1 = y_min + rec_wid*j
            df0 = df[df[:, 1] > x_min1]
            df1 = df0[df0[:, 1] <= (x_min1+rec_len)]
            df2 = df1[df1[:, 2] > y_min1]
            df3 = df2[df2[:, 2] <= (y_min1+rec_wid)]
            grid_num.append(len(df3))
    return grid_num
