
'''
空间kdtree+ 时间的等尺度
'''

import numpy as np
import matplotlib.pyplot as plt

a =[]
b =[]

class KDTree:
    def __init__(self, data, mins, maxs,split_point=None, largest_dim=None):
        self.data = np.asarray(data)
        self.elt = split_point      #   elt:数据点  
        self.split = largest_dim # split:划分域 
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
            #划分点
            split_point = 0.5*(self.data[int(N/2),largest_dim]+ self.data[int(N/2-1), largest_dim])
            # create subnodes
            mins1 = self.mins.copy()
            mins1[largest_dim] = split_point
            maxs2 = self.maxs.copy()
            maxs2[largest_dim] = split_point
            # Recursively build a KD-tree on each sub-node
            self.child1 = KDTree(self.data[int(N/2):], mins1, self.maxs)
            self.child2 = KDTree(self.data[:int(N/2)], self.mins, maxs2)
    def draw_rectangle(self, depth=None):
       
        if depth == 0:
            #rect = plt.Rectangle(self.mins, *self.sizes, ec='k',fc='none')
            a.append(self.mins)
            b.append(self.sizes)
         

        if self.child1 is not None:
            if depth is None:
                self.child1.draw_rectangle()
                self.child2.draw_rectangle()
            elif depth > 0:
                self.child1.draw_rectangle(depth - 1)
                self.child2.draw_rectangle( depth - 1)
                
def plot_opaque_cube(ax,x=10, y=20, z=30, dx=40, dy=50, dz=60,color='red'):
    #'alpha': 1,
    kwargs = { 'color': color}
    #ax.set_xlim(minx,maxx)
    #ax.set_ylim(miny,maxy)
    #ax.set_zlim(0,24)
    xx = np.linspace(x, x+dx,2)
    yy = np.linspace(y, y+dy,2 )
    zz = np.linspace(z, z+dz,2 )
    xx, yy = np.meshgrid(xx, yy)
    ax.plot_surface(xx, yy, z,**kwargs)
    ax.plot_surface(xx, yy, z+dz,**kwargs)
    yy, zz = np.meshgrid(yy, zz)
    ax.plot_surface(x, yy, zz,**kwargs)
    ax.plot_surface(x+dx, yy, zz,**kwargs)
    xx, zz = np.meshgrid(xx, zz)
    ax.plot_surface(xx, y, zz,**kwargs)
    ax.plot_surface(xx, y+dy, zz,**kwargs)
    
    
def draw_f7(df,sp1 ,sp2 ,fig):
    global a,b
    a = []
    b = []
    df[:,0] = (df[:,0] - min(df[:,0]))/60
    # 先空间的划分
    df0 = df[:,1:]
    KDT = KDTree(df0, [min(df0[:,0]), min(df0[:,1])], [max(df0[:,0]), max(df0[:,1])])
    KDT.draw_rectangle(depth= sp1)   
    split_num = []
    # 再时间上的划分
    cl = ['r','g','b','c','m','y','k','w']
    #fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.set_zlabel('时间/min')
    ax.set_title('先空间kdtree+时间等尺度')
    for i in range(len(a)):
        df0 = df[df[:,1]>a[i][0]]
        df1 = df0[df0[:,1]<=a[i][0] + b[i][0] ]
        df2 = df1[df1[:,2]>a[i][1]]
        df3 = df2[df2[:,2]<=a[i][1] + b[i][1]]
        #print(len(df3))
        df4 = df3[np.argsort(df3[:,0])]
        # 时间的划分
        time_split = list(range(0,len(df4),int(len(df4)/sp2)))
        time_split[-1] = len(df4)-1
        t_line = []
        for ts in time_split:
           # print(ts)
            t_line.append(df4[ts,0])
        t_line[0] = 0
        t_line[-1] = 1440
        for s in range(sp2-1):
            df5 = df4[df4[:,0]>t_line[s]]
            df6 = df5[df5[:,0]<=t_line[s+1]]
            split_num.append(len(df6))
        for j in range(len(t_line)-1):
            plot_opaque_cube(ax,x=a[i][0], y=a[i][1], z=t_line[j],
                              dx=b[i][0], dy=b[i][1], dz=t_line[j+1]-t_line[j],
                             color=np.random.choice(cl))
    return split_num



