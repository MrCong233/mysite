# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 09:47:58 2018

@author: admin
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def draw_fig(df, ax, sp):
    maxx = max(df[:, 1])
    minx = min(df[:, 1])
    maxy = max(df[:, 2])
    miny = min(df[:, 2])
    maxz = max(df[:, 0])
    minz = min(df[:, 0])

    xl = (maxx - minx) / sp
    yl = (maxy - miny) / sp
    zl = (maxz - minz) / sp
    col = ['r', 'b', 'w', 'g', 'c', 'y', 'm', 'k']
    #fig = plt.figure()
    #ax = Axes3D(fig)
    for i in range(sp):
        # print(i)
        for j in range(sp):
            for k in range(sp):
                x = minx + i*xl
                y = miny + j*yl
                z = 0 + k*zl
                cnum = i*sp * sp + j*sp + k
                c = cnum % 8
                plot_linear_cube(ax, x, y, z, xl, yl, zl, color=col[c])
    ax.set_title('3d_equal_grid')
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    ax.set_zlabel('time/s')


def plot_linear_cube(ax, x, y, z, dx, dy, dz, color='red'):
    xx = [x, x, x+dx, x+dx, x]
    yy = [y, y+dy, y+dy, y, y]
    kwargs = {'alpha': 1, 'color': color}
    ax.plot3D(xx, yy, [z]*5, **kwargs)
    ax.plot3D(xx, yy, [z+dz]*5, **kwargs)
    ax.plot3D([x, x], [y, y], [z, z+dz], **kwargs)
    ax.plot3D([x, x], [y+dy, y+dy], [z, z+dz], **kwargs)
    ax.plot3D([x+dx, x+dx], [y+dy, y+dy], [z, z+dz], **kwargs)
    ax.plot3D([x+dx, x+dx], [y, y], [z, z+dz], **kwargs)
    # plt.show()


def state_num(df, sp):

    maxx = max(df[:, 1])
    minx = min(df[:, 1])
    maxy = max(df[:, 2])
    miny = min(df[:, 2])
    maxz = max(df[:, 0])
    minz = min(df[:, 0])
    xl = (maxx - minx) / sp
    yl = (maxy - miny) / sp
    zl = (maxz - minz) / sp
    split_num = []
    for i in range(sp):
        for j in range(sp):
            for k in range(sp):
                dt0 = df[df[:, 1] > (minx + xl*i)]
                dt1 = dt0[dt0[:, 1] <= (minx + xl*(i+1))]
                dt2 = dt1[dt1[:, 2] > (miny + yl*j)]
                dt3 = dt2[dt2[:, 2] <= (miny + yl*(j+1))]
                dt4 = dt3[dt3[:, 0] > (minz + zl*k)]
                dt5 = dt4[dt4[:, 0] <= (minz + zl*(k+1))]
                split_num.append(len(dt5))
    return split_num
