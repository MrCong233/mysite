# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 15:29:17 2018

@author: admin
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os.path


def xifen(df, xs=50, ys=50, zs=30):
    '''
    细分
    小晶体内订单量的统计
    0     1      2     3     4     5     6     7     8     9    10    11
    minx  maxx  miny  maxy  minz  maxz  xloc  yloc  zloc  id    num  dist
    '''
    maxx = max(df[:, 1])
    minx = min(df[:, 1])
    maxy = max(df[:, 2])
    miny = min(df[:, 2])
    maxz = max(df[:, 0])
    minz = min(df[:, 0])

    xl = (maxx - minx) / xs
    yl = (maxy - miny) / ys
    zl = (maxz - minz) / zs

    st = np.zeros((xs*ys*zs, 12))
    for i in range(xs):
        # print(i)
        for j in range(ys):
            # print(j)
            for k in range(zs):
                row = i + j*xs + k*xs*ys
                st[row, 0] = minx + xl*i
                st[row, 1] = minx + xl*(i+1)
                st[row, 2] = miny + yl*j
                st[row, 3] = miny + yl*(j+1)
                st[row, 4] = minz + zl*k
                st[row, 5] = minz + zl*(k+1)
                st[row, 6] = i
                st[row, 7] = j
                st[row, 8] = k
                st[row, 9] = row
                dt0 = df[df[:, 1] >= (minx + xl*i)]
                dt1 = dt0[dt0[:, 1] < (minx + xl*(i+1))]
                dt2 = dt1[dt1[:, 2] >= (miny + yl*j)]
                dt3 = dt2[dt2[:, 2] < (miny + yl*(j+1))]
                dt4 = dt3[dt3[:, 0] >= (minz + zl*k)]
                dt5 = dt4[dt4[:, 0] < (minz + zl*(k+1))]
                st[row, 10] = len(dt5)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pd.DataFrame(st).to_csv(current_dir+'\\st.csv', index=None, header=None)


def hebing2(df):
    '''
    合并           
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    st1 = np.array(pd.read_csv(current_dir+'\\st.csv', header=None))
    h01 = np.zeros(len(st1))
    st1 = np.c_[st1, h01]  # 12列是合并状态
    merge = np.zeros((500, 500))  # 合并的立体 预计1w个
    v_num = []  # 每个网格点数统计
    i = 0
    new_id = len(st1)
    st2 = st1[st1[:, 12] == 0]
    while len(st2) > 0:
        # if i%100==0:print(i)
        # st2 = st1[st1[:, 12] == 0]  # 未合并的数据集
        # if len(st2) == 0:
        #     break
        minxid = st2[0, 6]
        minyid = st2[0, 7]
        minzid = st2[0, 8]
        st2[:, 11] = np.abs(st2[:, 6] - minxid) + \
            np.abs(st2[:, 7] - minyid) + np.abs(st2[:, 8] - minzid)

        st2 = st2[np.argsort(st2[:, 11])]
        id0 = st2[0, 9]
        merge[i, 0] = id0
        st1[st1[:, 9] == id0, 12] = 1  # 已合并
        v_num = st2[0, 10]  # 合并之后的总量
        j = 0
        while j < 500:

            if v_num == 12:
                i += 1
                break
            if v_num > 12:
                grid_info = st2[st2[:, 9] == id0]
                df_grid0 = df[df[:, 1] > grid_info[0, 0]]
                df_grid1 = df_grid0[df_grid0[:, 1] <= grid_info[0, 1]]
                df_grid2 = df_grid1[df_grid1[:, 2] > grid_info[0, 2]]
                df_grid3 = df_grid2[df_grid2[:, 2] <= grid_info[0, 3]]
                df_grid4 = df_grid3[df_grid3[:, 0] > grid_info[0, 4]]
                df_grid5 = df_grid4[df_grid4[:, 0] <= grid_info[0, 5]]
                df_grid6 = df_grid5[np.argsort(df_grid5[:, 1])]
                dnum = 12-(v_num-grid_info[0, 10])  # 缺少的数量
                spx = df_grid6[int(dnum)-1, 1]  # 新分割线
                st1[st1[:, 9] == id0, 1] = spx
                st1[st1[:, 9] == id0, 10] = dnum
                st2[st2[:, 9] == id0, 1] = spx
                st2[st2[:, 9] == id0, 10] = dnum
                grid_info[0, 0] = spx
                grid_info[0, 9] = new_id
                new_id += 1
                grid_info[0, 12] = 0
                df_g0 = df[df[:, 1] > grid_info[0, 0]]
                df_g1 = df_g0[df_g0[:, 1] <= grid_info[0, 1]]
                df_g2 = df_g1[df_g1[:, 2] > grid_info[0, 2]]
                df_g3 = df_g2[df_g2[:, 2] <= grid_info[0, 3]]
                df_g4 = df_g3[df_g3[:, 0] > grid_info[0, 4]]
                df_g5 = df_g4[df_g4[:, 0] <= grid_info[0, 5]]
                grid_info[0, 10] = len(df_g5)
                st1[st1[:, 9] == id0, 12] = 1  # 已合并
                st1 = np.vstack([st1, grid_info])
                i += 1
                break
            j += 1
            if j == 500:
                i += 1
                break
            if len(st2) == j:
                break
            id0 = st2[j, 9]
            st1[st1[:, 9] == id0, 12] = 1
            v_num += st2[j, 10]
            merge[i, j] = id0
        st2 = st1[st1[:, 12] == 0]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pd.DataFrame(merge).to_csv(
        current_dir+'\\merge.csv', index=None, header=None)
    pd.DataFrame(st1).to_csv(current_dir+'\\st1.csv', index=None, header=None)


def state_num():
    '''
    统计每个数据块内点的个数
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    merge = np.array(pd.read_csv(current_dir+'\\merge.csv', header=None))
    merge1 = merge[merge[:, 0] != 0]
    st1 = np.array(pd.read_csv(current_dir+'\\st1.csv', header=None))
    order_num = []
    for i in range(len(merge1)):
        gridid = merge1[i, :]
        g_id = gridid[gridid[:] != 0]
        num = 0
        for j in range(len(g_id)):
            num += st1[st1[:, 9] == g_id[j], 10][0]
        order_num.append(num)

    return order_num


def plot_opaque_cube(ax, x=10, y=20, z=30, dx=40, dy=50, dz=60, color='red'):
    #'alpha': 1,
    '''
    画长方体
    '''
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


def draw_fig(df, sp, fig):
    maxx = max(df[:, 1])
    minx = min(df[:, 1])
    maxy = max(df[:, 2])
    miny = min(df[:, 2])
    #maxz = max(df[:,0])
    minz = min(df[:, 0])
    cl = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    merge3 = np.array(pd.read_csv(current_dir+'\\merge.csv', header=None))
    st = np.array(pd.read_csv(current_dir+'\\st1.csv', header=None))
    st[:, :4] = st[:, :4]  # *1000000
    st[:, 4:6] = (st[:, 4:6] - minz)
    c0 = 0
    #fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    ax.set_zlabel('time/s')
    for i in range(sp):  # len(merge3)
        #i= 4567
        m0 = merge3[i, :]
        c = c0 % 8
        c0 += 1
        m1 = m0[m0 != 0]
        #if i == 0:m1 = m0[:45]
        for j in range(len(m1)):
            dt00 = st[st[:, 9] == m1[j]]
            x = (dt00[0, 0])
            y = (dt00[0, 2])
            z = (dt00[0, 4])
            dx = (dt00[0, 1] - dt00[0, 0])
            dy = (dt00[0, 3] - dt00[0, 2])
            dz = (dt00[0, 5] - dt00[0, 4])
            plot_opaque_cube(ax, x, y, z, dx, dy, dz, color=cl[c])
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_zlim(0, 86400)
    ax.set_title("slice_merge")
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    # plt.show()
