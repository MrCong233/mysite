# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 16:47:51 2019

@author: HelpMe
"""

import osmnx as ox
import networkx as nx
import pyproj
import numpy as np
import os.path
from collections import OrderedDict
from shapely.strtree import STRtree
from collections import namedtuple
from . import cache


# print('load road')
# CPointRec = namedtuple('CPointRec', ["log_x", "log_y", "p_x", "p_y", "road_id", "log_id",
                                    #  "source", "target", "weight", "fraction", "v", "log_time", "track_id", "car_id"])

MAX_V=50
MAX_DIS=5000
ROAD_GRAPH=None


def init_road_graph():
    global ROAD_GRAPH
    _, edges=simple_G()
    road_graph=nx.DiGraph()
    for _, row in edges.iterrows():
        road_id=row['road_id']
        source=row['u_replace']
        target=row['v_replace']
        weight=row['length']
        road_graph.add_edge(source, target, weight = weight, road_id = road_id)
    ROAD_GRAPH=road_graph


def lonlat2log(GPS_tri):
    '''
    转换GPS轨迹数据形式
    '''
    '''
    pyproj 用来转化WGS84坐标到投影坐标
    '''
    p1_proj=pyproj.Proj(init = "epsg:4326")  # 定义数据地理坐标系 WGS84
    p2_proj=pyproj.Proj(init = "epsg:32648")  # 定义转换投影坐标系
    data=GPS_tri.copy()
    data['uuid']=list(range(len(data)))
    TrackRec=namedtuple('TrackRec', ['x', 'y', 'uuid', 'log_time'])
    logs=[]
    for _, row in data.iterrows():
        row['x'], row['y']=pyproj.transform(
            p1_proj, p2_proj, row['x'], row['y'])
        logs.append(TrackRec(
            row['x'],
            row['y'],
            row['uuid'],
            row['time']))
    return logs


def GCJ2WGS(lon, lat):
    '''
    火星坐标转换成WGS84坐标
    '''
    a = 6378245.0  # 克拉索夫斯基椭球参数长半轴a
    ee = 0.00669342162296594323  # 克拉索夫斯基椭球参数第一偏心率平方
    PI = 3.14159265358979324  # 圆周率
    # 以下为转换公式
    x = lon - 105.0
    y = lat - 35.0
    # 经度
    dLon = 300.0 + x + 2.0 * y + 0.1 * x * \
        x + 0.1 * x * y + 0.1 * np.sqrt(abs(x))
    dLon += (20.0 * np.sin(6.0 * x * PI) + 20.0 *
             np.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLon += (20.0 * np.sin(x * PI) + 40.0 * np.sin(x / 3.0 * PI)) * 2.0 / 3.0
    dLon += (150.0 * np.sin(x / 12.0 * PI) + 300.0 *
             np.sin(x / 30.0 * PI)) * 2.0 / 3.0
    # 纬度
    dLat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * \
        y * y + 0.1 * x * y + 0.2 * np.sqrt(abs(x))
    dLat += (20.0 * np.sin(6.0 * x * PI) + 20.0 *
             np.sin(2.0 * x * PI)) * 2.0 / 3.0
    dLat += (20.0 * np.sin(y * PI) + 40.0 * np.sin(y / 3.0 * PI)) * 2.0 / 3.0
    dLat += (160.0 * np.sin(y / 12.0 * PI) + 320 *
             np.sin(y * PI / 30.0)) * 2.0 / 3.0
    radLat = lat / 180.0 * PI
    magic = np.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = np.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * np.cos(radLat) * PI)
    wgsLon = lon - dLon
    wgsLat = lat - dLat
    return [wgsLon, wgsLat]


def simple_G():
    '''
        删除长度为0 的边
    '''
    current_dir = os.path.dirname(os.path.abspath(__file__))
    G_proj = ox.load_graphml(current_dir + '\\data\\chengdu_proj.graphml')
    nodes, edges = ox.graph_to_gdfs(G_proj, fill_edge_geometry=True)
    edges = edges[edges['u'] != edges['v']]
    edges = edges[edges['key'] == 0]
    edges = edges[edges['length'] > 0]
    nodes['osmid'] = [int(i) for i in nodes['osmid']]
    nodes['node_id'] = range(nodes.shape[0])
    edges['road_id'] = range(edges.shape[0])
    '''
        nodes_replace_id_dict 已经保存
    '''
    # 读取
    f = open(current_dir + '\\data\\nodes_replace_id_dict.txt', 'r')
    a = f.read()
    nodes_replace_id_dict = eval(a)
    f.close()
    edges['u_replace'] = [nodes_replace_id_dict[i] for i in edges['u']]
    edges['v_replace'] = [nodes_replace_id_dict[i] for i in edges['v']]
    G = ox.gdfs_to_graph(nodes, edges)
    return G, edges


def get_GandRtree():
    G, edges = simple_G()
    coord_feature_dict = {}
    geom_list = []
    for _, row in edges.iterrows():
        xs, ys = row['geometry'].xy
        geometry = {'coordinates': list(zip(xs, ys)),
                    'type': 'LineString'}
        geom = row['geometry']
        geom_list.append(geom)
        coord_key = geom.coords[0] + geom.coords[-1]
        assert(coord_key not in coord_feature_dict)
        coord_feature_dict[coord_key] = \
            {'geometry': geometry,
             'id': row['road_id'],
             'properties': OrderedDict([('source', row['u_replace']),
                                        ('target', row['v_replace']),
                                        ('weight', row['length'])]),
             'type': 'Feature'}
    rtree = STRtree(geom_list)
    G_copy = nx.MultiDiGraph()
    G_copy.graph = G.graph
    for _, data in G.nodes(data=True):
        G_copy.add_node(data['node_id'], **data)
    edges = [(data['u_replace'], data['v_replace'], data)
             for u, v, data in G.edges(data=True)]
    G_copy.add_edges_from(edges)
    return G_copy, rtree, coord_feature_dict


'''

获得两点间的dijkstra距离

'''


def get_dijkstra_distance(pre_closest_point, now_closest_point, cufoff=5000):

    if (ROAD_GRAPH is None):
        # print('init road_graph')
        init_road_graph()

    '''
    获得两个点之间的dijkstra距离

    如果两个点之间的距离>cufoff，则认为两点之间的距离为MAX_DIS，这个操作是为了提高效率。

    Parameters:
    -----------
    pre_closest_point : CPointRec
        起点
    now_closest_point : CPointRec
        终点

    '''

    pre_road_id = pre_closest_point.road_id
    pre_source = pre_closest_point.source
    pre_target = pre_closest_point.target
    pre_fraction = pre_closest_point.fraction
    pre_weight = pre_closest_point.weight

    assert(ROAD_GRAPH[pre_source][pre_target]['weight'] == pre_weight)

    now_road_id = now_closest_point.road_id
    now_source = now_closest_point.source
    now_target = now_closest_point.target
    now_fraction = now_closest_point.fraction
    now_weight = now_closest_point.weight

    assert(ROAD_GRAPH[now_source][now_target]['weight'] == now_weight)

    source_id = cache.get_unique_id(pre_road_id, pre_fraction)  # 唯一标识一个起点
    target_id = cache.get_unique_id(now_road_id, now_fraction)  # 唯一标识一个终点

    # if cached
    result = cache.get_distance_from_cache(source_id, target_id)
    if result:
        # print('from cache')
        return result[0]

    # if not cached
    if pre_road_id == now_road_id:
        if now_fraction <= pre_fraction:
            cache.save_distance_to_cache(
                source_id, target_id, MAX_DIS, None, None)
            return MAX_DIS
        else:
            dis = (now_fraction-pre_fraction) * now_weight
            cache.save_distance_to_cache(source_id, target_id, dis, [
                'a', 'b'], [pre_road_id])
            return dis

    pre_id = 'a'
    now_id = 'b'

    if pre_fraction == 0:
        pre_id = pre_source
    elif pre_fraction == 1:
        pre_id = pre_target
    else:
        ROAD_GRAPH.add_edge(
            pre_source, pre_id, weight=pre_fraction * pre_weight, road_id=pre_road_id)
        ROAD_GRAPH.add_edge(pre_id, pre_target, weight=(
            1-pre_fraction) * pre_weight, road_id=pre_road_id)

    if now_fraction == 0:
        now_id = now_source
    elif now_fraction == 1:
        now_id = now_target
    else:
        ROAD_GRAPH.add_edge(
            now_source, now_id, weight=now_fraction * now_weight, road_id=now_road_id)
        ROAD_GRAPH.add_edge(now_id, now_target, weight=(
            1-now_fraction) * now_weight, road_id=now_road_id)

    dis = MAX_DIS
    vertex_path = None

    length, path = nx.single_source_dijkstra(ROAD_GRAPH, pre_id, cutoff=cufoff)
    try:
        dis = length[now_id]
        vertex_path = path[now_id]
    except KeyError:
        pass
    if vertex_path is None:
        cache.save_distance_to_cache(source_id, target_id, dis, None, None)
    else:
        road_path = ['x']
        for i in range(1, len(vertex_path)):
            pre_vertex = vertex_path[i-1]
            now_vertex = vertex_path[i]
            road_id = ROAD_GRAPH[pre_vertex][now_vertex]['road_id']
            if road_id != road_path[-1]:
                road_path.append(road_id)

        cache.save_distance_to_cache(source_id, target_id, dis,
                                     vertex_path, road_path[1:])
    if pre_fraction != 0 and pre_fraction != 1:
        ROAD_GRAPH.remove_edge(pre_source, pre_id)
        ROAD_GRAPH.remove_edge(pre_id, pre_target)
    if now_fraction != 0 and now_fraction != 1:
        ROAD_GRAPH.remove_edge(now_source, now_id)
        ROAD_GRAPH.remove_edge(now_id, now_target)
    return dis


def get_connected_path(match_point_list):
    '''
    获得match_list对应的connected vertex path和connected road path

    Parameters:
    -------------
    match_point_list : list
        匹配好的点列表
    Returns:
    ----------
    connected_vertex_path : list
        轨迹按顺序经过的vertex
    connected_road_path : list
        轨迹按顺序经过的road

    '''
    pre_point = match_point_list[0]
    connected_vertex_path = ['x']
    connected_road_path = ['x']
    for now_point in match_point_list[1:]:
        source_id = cache.get_unique_id(pre_point.road_id, pre_point.fraction)
        target_id = cache.get_unique_id(now_point.road_id, now_point.fraction)
        result = cache.get_distance_from_cache(source_id, target_id)
        assert(result is not None)
        dis, vertex_path, road_path = result
        assert(vertex_path is not None)
        assert(road_path is not None)
        elapse_time = (now_point.log_time - pre_point.log_time).total_seconds()
        if elapse_time * MAX_V < dis:
            return None, None  # 超速行驶
        for vertex in vertex_path:
            if vertex in ['a', 'b']:
                continue
            else:
                if vertex != connected_vertex_path[-1]:
                    connected_vertex_path.append(int(vertex))
        for road in road_path:
            if road != connected_road_path[-1]:
                connected_road_path.append(int(road))
        pre_point = now_point

    return connected_vertex_path[1:], connected_road_path[1:]
