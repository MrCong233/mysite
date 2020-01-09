# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 22:14:11 2018

@author: admin
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


class KDTree:
    # class initialization function
    def __init__(self, data, mins, maxs):
        self.data = np.asarray(data)
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
            # sort on the dimension with the largest spread
            largest_dim = np.argmax(self.sizes)
            i_sort = np.argsort(self.data[:, largest_dim])
            self.data[:] = self.data[i_sort, :]

            # find split point
            N = self.data.shape[0]
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
        """Recursively plot a visualization of the KD tree region"""
        if depth == 0:
            rect = plt.Rectangle(self.mins, *self.sizes, ec='k', fc='none')
            ax.add_patch(rect)
            a.append(self.mins)
            b.append(self.sizes)
        if self.child1 is not None:
            if depth is None:
                self.child1.draw_rectangle(ax)
                self.child2.draw_rectangle(ax)

            elif depth > 0:
                self.child1.draw_rectangle(ax, depth - 1)
                self.child2.draw_rectangle(ax, depth - 1)


a = []
b = []


def draw_fig(df, ax, sp):
    X = df[:, 1:]
    x = X[:, 0]
    y = X[:, 1]
    global a
    global b
    a = []
    b = []
    KDT = KDTree(X, [min(x), min(y)], [max(x), max(y)])

    ax.scatter(X[:, 0], X[:, 1], s=1)
    KDT.draw_rectangle(ax, depth=sp)
    ax.set_xlabel('longitude')
    # ax.set_xlabel('经度')
    ax.set_ylabel('latitude')
    # ax.set_ylabel('维度')
    ax.set_title('2d_kdtree')
    # print('a:',len(a))

    split_num = []
    for i in range(len(a)):
        minx = a[i][0]
        miny = a[i][1]
        maxx = minx + b[i][0]
        maxy = miny + b[i][1]
        df0 = df[df[:, 1] > minx]
        df1 = df0[df0[:, 1] <= maxx]
        df2 = df1[df1[:, 2] > miny]
        df3 = df2[df2[:, 2] <= maxy]
        split_num.append(len(df3))

    return split_num
