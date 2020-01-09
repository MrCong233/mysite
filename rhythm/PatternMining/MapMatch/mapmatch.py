# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 11:19:42 2019

@author: HelpMe
"""

from collections import namedtuple, defaultdict
from shapely.geometry import Point
from . import core
from . import MyTool
CPointRec = namedtuple('CPointRec', ["log_x", "log_y", "p_x", "p_y",
                                     "road_id", "log_id", "source",
                                     "target", "weight", "fraction",
                                     "log_time"])


def get_closest_points(log, road_rtree, coord_feature_dict):
    '''
    获得点在路网中的投影点

    Parameters:
    -------------
    point : shapely point
        gps log点
    road_tree : shapely rtree
        道路rtree
    coord_feature_dict : dict
        道路头尾坐标 -> 道路feature字典

    '''
    # begin_tick = time.time()
    point = Point(log.x, log.y)
    point_buffer = point.buffer(20)
    project_roads = []
    for road in road_rtree.query(point_buffer):
        if road.intersects(point_buffer):
            project_roads.append(road)

    project_points = []
    for road in project_roads:
        fraction = road.project(point, normalized=True)
        project_point = road.interpolate(fraction, normalized=True)
        road_feature = coord_feature_dict[road.coords[0]+road.coords[-1]]
        project_points.append(CPointRec(
            log.x,
            log.y,
            project_point.x,
            project_point.y,
            int(road_feature['id']),
            log.uuid,
            road_feature['properties']['source'],
            road_feature['properties']['target'],
            road_feature['properties']['weight'],
            fraction,
            log.log_time))
    return project_points
#%%


def map_match_log(logs, road_rtree, coord_feature_dict):
    '''
    trace 
        轨迹数据
        |car_id|lon|lat|log_time|track_id|
    '''
    log_closest_points = defaultdict(list)

    for log in logs:

        project_points = get_closest_points(
            log, road_rtree, coord_feature_dict)
        if len(project_points) > 0:
            log_closest_points[log.uuid] = project_points

    log_list = [i for i in log_closest_points.keys()]
    if not log_list:
        return None, None
#    clear_cache()
    match_point_list = core.match_until_connect(log_list, log_closest_points)
    if match_point_list:
        connected_vertex_path,  connected_road_path = MyTool.get_connected_path(
            match_point_list)
        return connected_vertex_path, connected_road_path
    else:
        return None, None
