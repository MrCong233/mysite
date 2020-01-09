# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 11:23:13 2018

@author: admin
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from itertools import product, combinations 

xaxis = []
yaxis = []
zaxis = []
color = ['b','r','k','y','g','m']
class KDTree:
    def __init__(self, data, mins, maxs,i0):
        self.data = np.asarray(data)

        if mins is None:
            mins = data.min(0)
        if maxs is None:
            maxs = data.max(0)
        if i0 is None:
            i0 = 0
        self.mins = np.asarray(mins)
        self.maxs = np.asarray(maxs)
        self.sizes = self.maxs - self.mins

        self.child1 = None
        self.child2 = None

        if len(data) > 10:
            
            #largest_dim= i0 % 3   #顺序选择维度策略   
            #largest_dim = np.random.randint(3)#随机选择维度
            #定制版维度
            dim = [0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2]       
            largest_dim = dim[i0]
            i0 += 1
            
            i_sort = np.argsort(self.data[:, largest_dim])
            self.data[:] = self.data[i_sort, :]

            # find split point
            N = self.data.shape[0]
            split_point = self.data[int(N/2),largest_dim]

            # create subnodes
            mins1 = self.mins.copy()
            mins1[largest_dim] = split_point
            maxs2 = self.maxs.copy()
            maxs2[largest_dim] = split_point

            # Recursively build a KD-tree on each sub-node
            self.child1 = KDTree(self.data[int(N/2):], mins1, self.maxs,i0)
            self.child2 = KDTree(self.data[:int(N/2)], self.mins, maxs2,i0)
            
    def draw_rectangle(self, ax, depth=None):
        if depth == 0:
            h0 = [self.mins[0],(self.mins[0]+self.sizes[0])]
            h1 = [self.mins[1],(self.mins[1]+self.sizes[1])]
            h2 = [self.mins[2],(self.mins[2]+self.sizes[2])]
            xaxis.append(h0)
            yaxis.append(h1)
            zaxis.append(h2)
            #fig = plt.figure(1)
            #ax = fig.gca(projection='3d')
            cl = np.random.randint(0,6)
            for s, e in combinations(np.array(list(product(h0,h1,h2))), 2):   
                if np.sum(np.abs(s-e)) == h0[1]-h0[0]:
                    ax.plot3D(*zip(s,e), color=color[cl])
                    #xaxis.append(h0)
                if np.sum(np.abs(s-e)) == h1[1]-h1[0]:
                    ax.plot3D(*zip(s,e), color=color[cl])   
                if np.sum(np.abs(s-e)) == h2[1]-h2[0]:
                    ax.plot3D(*zip(s,e), color=color[cl])  
            # plt.show()                 
            
        if self.child1 is not None:
            if depth is None:
                self.child1.draw_rectangle(ax)
                self.child2.draw_rectangle(ax)
            elif depth > 0:
                self.child1.draw_rectangle(ax, depth - 1)
                self.child2.draw_rectangle(ax, depth - 1)

def draw_fig(df,sp,ax):
    global xaxis
    global yaxis
    global zaxis
    xaxis = []
    yaxis = []
    zaxis = []
    data = df[:,[1,2,0]]
    data[:,2] = data[:,2] - min(data[:,2])
    KDT = KDTree(data,mins=data.min(0),  maxs = data.max(0),i0=None)
    
    #ax.scatter(data[:, 0], data[:, 1],data[:,2],s=5)
    ax.set_zlabel('time/s')  
    ax.set_ylabel('latitude')
    ax.set_xlabel('longitude')    
    depth =  sp # 划分深度
    KDT.draw_rectangle(ax, depth)
    ax.set_title('3dtree_depth:'+str(depth))
    
    split_num = []
    for i in range(len(xaxis)):
        df0 = data[data[:,0]>xaxis[i][0]]
        df1=df0[df0[:,0]<=xaxis[i][1]]
        df2 = df1[df1[:,1]>yaxis[i][0]]
        df3 = df2[df2[:,1]<=yaxis[i][1]]
        df4 = df3[df3[:,2]>zaxis[i][0]]
        df5 = df4[df4[:,2]<=zaxis[i][1] ]
        split_num.append(len(df5))
        
    return split_num