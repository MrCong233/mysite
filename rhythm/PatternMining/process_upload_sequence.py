import os.path
from timeit import default_timer
from traceback import format_exc
from datetime import datetime
from csv import writer
from pyproj import Proj, transform
from pandas import read_csv, to_datetime, DataFrame
from MapMatch import MyTool, mapmatch


def match_rule(result, G_copy):
    rules = {}
    p1_proj = Proj(init="epsg:4326")  # WGS84 coordinates system
    p2_proj = Proj(init="epsg:32648")  # projection coordinates system
    networks_edges = {data['road_id']: data for _,
                      _, data in G_copy.edges(data=True)}
    result = [id for l in result for id in l]
    for road_id in result:
        road_line_string = networks_edges[road_id]['geometry']
        road_wgs84_coords = []
        for coord in list(road_line_string.coords):
            road_wgs84_coords.append(transform(
                p2_proj, p1_proj, coord[0], coord[1]))
        if 'name' in networks_edges[road_id]:
            rules["{}".format(road_id)] = {
                'road_name': networks_edges[road_id]['name'],
                'road_length': networks_edges[road_id]['length'],
                'road_coords': road_wgs84_coords,
            }
            # rules.append(road_info)
    return rules


def map_match_result(traj_df, file_path):
    # match_df = traj_df.copy()
    result = []
    match_df = traj_df.rename(
        columns={'date_time': 'time', 'latitude': 'y', 'longitude': 'x', 'traj_num': 'id'})
    match_df['time'] = to_datetime(match_df['time'])
    G_copy, road_rtree, coord_feature_dict = MyTool.get_GandRtree()
    u_id = match_df['id'].unique().tolist()
    for u in u_id:
        traj = match_df[match_df['id'] == u][['x', 'y', 'time']]
        logs = MyTool.lonlat2log(traj)
        _, road_path = mapmatch.map_match_log(
            logs, road_rtree, coord_feature_dict)
        if road_path is not None:
            if road_path != []:
                result.append(road_path)
    data_range = {
        'traj_num_range': list(match_df['id'].unique()),
    }
    rules = match_rule(result, G_copy)
    with open(file_path, 'w+') as file:
        file_data = writer(file, delimiter=' ', quotechar='\r')
        for row in result:
            file_data.writerow(row)
    return data_range, rules


def grid_number(point, latitude_pair, longitude_pair, height, width):
    row_height = (latitude_pair[1] - latitude_pair[0]) / height
    coln_width = (longitude_pair[1] - longitude_pair[0]) / width
    row_count = (point[0] - latitude_pair[0]) // row_height
    coln_count = (point[1] - longitude_pair[0]) // coln_width
    rtn_num = int(row_count * width + coln_count + 51)
    # print(type(rtn_num))
    return rtn_num


def equal_grid_result(df, height, width, file_path):
    min_lat = df['latitude'].min()
    max_lat = df['latitude'].max()
    min_lon = df['longitude'].min()
    max_lon = df['longitude'].max()
    df['p_num'] = df.apply(lambda row: grid_number(
        (row['latitude'], row['longitude']),
        (min_lat, max_lat), (min_lon, max_lon),
        height, width), axis=1)
    # save to csv
    with open(file_path, 'w+') as file:
        file_data = writer(file, delimiter=' ', quotechar='\r')
        for _, group in df.groupby(['traj_num']):
            file_data.writerow(group['p_num'].tolist())
    data_range = {
        'traj_num_range': list(df['traj_num'].unique()),
        'grid_num_range': list(df['p_num'].unique() - 51),
    }
    rules = {}
    return data_range, rules

# TODO change input and output file, also  try and exception record should add the file info.


def process_original_traj(grid_or_not=True, height=10, width=10):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        start = default_timer()
        df = read_csv(current_dir + "\\dataset\\" +
                      "upload_sequence_original.csv")
        # specified 4 headers
        keys = df.keys()
        if("traj_num" not in keys or "latitude" not in keys or
                "longitude" not in keys or "date_time" not in keys):
            # return 1
            raise KeyError(
                "Lack of one or all specified keys, please check traj_num, date_time, latitude, longitude")
        df = df[~df.isnull().any(axis=1)]
        # specified shape without null value
        row_count, column_count = df.shape
        if(row_count < 1024 or column_count != 4):
            # return 1
            raise IndexError(
                "Number of records without null value is less than 1024 or columns count is not 4.")
        # sampling
        df = df.sample(n=1024)
        # sort by timestamp
        df = df.sort_values(by=['traj_num', 'date_time'])
        file_path = '{}\\dataset\\upload_sequence_processed.txt'.format(
            current_dir)
        if grid_or_not == True:
            data_range, rules = equal_grid_result(df, height, width, file_path)
        else:
            data_range, rules = map_match_result(df, file_path)
        stop = default_timer()
        run_time = stop - start
        results = {
            'date_time': [current_date_time],
            'run_time': [run_time]
        }
        new_row = DataFrame(results)
        file_path = '{}\\try_process_upload_sequence\\try_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
        return 0, data_range, rules
    except:
        # print(format_exc())
        results = {
            'date_time': current_date_time,
            'exception_info': format_exc()
        }
        # print(results)
        new_row = DataFrame(results, index=[0])
        file_path = '{}\\except_process_upload_sequence\\except_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
        data_range = {}
        rules = {}
        return 1, data_range, rules


# print(process_original_traj(grid_or_not=True, height=10, width=10))
# print(process_original_traj(grid_or_not=False))

# current_dir = os.path.dirname(os.path.abspath(__file__))

# df = read_csv(current_dir + "\\dataset\\" +
#               "upload_sequence_original.csv")
# df = df.sort_values(by=['traj_num', 'date_time'])
# file_path = '{}\\dataset\\upload_sequence_processed.txt'.format(
#             current_dir)
# # # print(df)
# print(map_match_result(df, file_path))
