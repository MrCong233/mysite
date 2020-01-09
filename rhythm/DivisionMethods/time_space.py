# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 20:03:18 2018

@author: admin
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

a = []
b = []
'''
先时间再空间的切分
'''


def time_split(data, sp_num=24):  # 切分次数
    data = data[data[:, 0].argsort()]  # 按时间排序
    N_t = len(data)  # 数据总量
    row = np.arange(0, N_t, int(N_t/sp_num))
    row = np.append(row, N_t-1)
    time_num = data[row, 0]
    run_times = sp_num  # 按时间切分数据被分为 run_times 次
    return run_times, row, time_num  # 返回切分次数，运行时间


class KDTree:
    def __init__(self, data, mins, maxs, split_point=None, largest_dim=None):
        self.data = np.asarray(data)
        self.elt = split_point  # elt:数据点
        self.split = largest_dim  # split:划分域
        # data should be two-dimensional
        assert self.data.shape[1] == 2
        if mins is None:
            mins = data.min(0)
        if maxs is None:
            maxs = data.max(0)
        self.mins = np.asarray(mins)
        self.maxs = np.asarray(maxs)
        self.sizes = self.maxs - self.mins
        self.child1 = None
        self.child2 = None
        if len(data) > 1:
            # 划分域
            largest_dim = np.argmax(self.sizes)
            i_sort = np.argsort(self.data[:, largest_dim])
            self.data[:] = self.data[i_sort, :]

            N = self.data.shape[0]
            # 划分点
            split_point = 0.5 * \
                (self.data[int(N/2), largest_dim] +
                 self.data[int(N/2-1), largest_dim])
            # create subnodes
            mins1 = self.mins.copy()
            mins1[largest_dim] = split_point
            maxs2 = self.maxs.copy()
            maxs2[largest_dim] = split_point
            # Recursively build a KD-tree on each sub-node
            self.child1 = KDTree(self.data[int(N/2):], mins1, self.maxs)
            self.child2 = KDTree(self.data[:int(N/2)], self.mins, maxs2)

    def draw_rectangle(self, ax, depth=None):

        if depth == 0:
            rect = plt.Rectangle(self.mins, *self.sizes, ec='k', fc='none')
            a.append(self.mins)
            b.append(self.sizes)
            ax.add_patch(rect)

        if self.child1 is not None:
            if depth is None:
                self.child1.draw_rectangle(ax)
                self.child2.draw_rectangle(ax)
            elif depth > 0:
                self.child1.draw_rectangle(ax, depth - 1)
                self.child2.draw_rectangle(ax, depth - 1)


def draw_fig(df, sp1, sp2, fig):
    global a
    global b
    data = df
    run_time, row, time_num = time_split(data, sp_num=sp1)  # 时间域划分深度
    i = 1
    a = []
    b = []
    df0 = data[row[i]:row[i+1], 1:]
    #fig = plt.figure(i)
    ax = fig.add_subplot(1, 2, 2)
    KDT = KDTree(df0, [min(df0[:, 0]), min(df0[:, 1])],
                 [max(df0[:, 0]), max(df0[:, 1])])
    ax.scatter(df0[:, 0], df0[:, 1], s=1)
    KDT.draw_rectangle(ax, depth=sp2)  # 空间域划分深度
    ax.set_title('time_slice+kdtree')
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')

    z0 = (time_num - min(data[:, 0]))/3600
    cl = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    #ax1 = fig.gca()
    ax1.set_xlabel('longitude')
    ax1.set_ylabel('latitude')
    ax1.set_zlabel('time/h')
    ax1.set_title('time_slice')
    for i in range(len(z0)-1):
        z1 = z0[i]
        dz1 = z0[i+1] - z0[i]
        plot_opaque_cube(ax1, x=min(data[:, 1]), y=min(
            data[:, 2]), z=z1, dx=1, dy=1, dz=dz1, color=cl[i % 8])

    split_num = []
    for i in range(len(a)):
        minx = a[i][0]
        miny = a[i][1]
        maxx = minx + b[i][0]
        maxy = miny + b[i][1]
        df1 = df0[df0[:, 0] > minx]
        df2 = df1[df1[:, 0] <= maxx]
        df3 = df2[df2[:, 1] > miny]
        df4 = df3[df3[:, 1] <= maxy]
        split_num.append(len(df4))
        # print(len(df3))
    return split_num


def plot_opaque_cube(ax, x=10, y=20, z=30, dx=40, dy=50, dz=60, color='red'):
    #'alpha': 1,
    kwargs = {'color': color}
    # ax.set_xlim(minx,maxx)
    # ax.set_ylim(miny,maxy)
    # ax.set_zlim(0,24)
    xx = np.linspace(x, x+dx, 2)
    yy = np.linspace(y, y+dy, 2)
    zz = np.linspace(z, z+dz, 2)
    xx, yy = np.meshgrid(xx, yy)
    # ax.plot_surface(xx, yy, z, **kwargs)
    # ax.plot_surface(xx, yy, z+dz, **kwargs)
    yy, zz = np.meshgrid(yy, zz)
    ax.plot_surface(x, yy, zz, **kwargs)
    ax.plot_surface(x+dx, yy, zz, **kwargs)
    xx, zz = np.meshgrid(xx, zz)
    ax.plot_surface(xx, y, zz, **kwargs)
    ax.plot_surface(xx, y+dy, zz, **kwargs)
