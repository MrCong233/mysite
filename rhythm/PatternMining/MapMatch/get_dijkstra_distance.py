
'''

获得两点间的dijkstra距离

'''

print('load road')
from collections import namedtuple
import networkx as nx
from . import cache
# get_distance_from_cache, save_distance_to_cache, get_unique_id
from . import MyTool

CPointRec = namedtuple('CPointRec', ["log_x", "log_y", "p_x", "p_y", "road_id", "log_id",
                                     "source", "target", "weight", "fraction", "v", "log_time", "track_id", "car_id"])

MAX_V = 33
MAX_DIS = 5000
ROAD_GRAPH = None


def init_road_graph():
    global ROAD_GRAPH
    G, edges = MyTool.simple_G()
    road_graph = nx.DiGraph()
    for index, row in edges.iterrows():
        road_id = row['road_id']
        source = row['u_replace']
        target = row['v_replace']
        weight = row['length']
        road_graph.add_edge(source, target, weight=weight, road_id=road_id)
    ROAD_GRAPH = road_graph


def get_dijkstra_distance(pre_closest_point, now_closest_point, cufoff=5000):

    if (ROAD_GRAPH is None):
        print('init road_graph')
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
