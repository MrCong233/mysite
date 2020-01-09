import os.path
from timeit import default_timer
from traceback import format_exc
from datetime import datetime
from pandas import read_csv, to_datetime, DataFrame


def grid_number(point, latitude_pair, longitude_pair, height, width):
    row_height = (latitude_pair[1] - latitude_pair[0]) / height
    coln_width = (longitude_pair[1] - longitude_pair[0]) / width
    row_count = (point[0] - latitude_pair[0]) // row_height
    coln_count = (point[1] - longitude_pair[0]) // coln_width
    rtn_num = int(row_count * width + coln_count + 51)
    # print(type(rtn_num))
    return rtn_num


def process_original_od(height, width):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        start = default_timer()
        df = read_csv(current_dir + "\\dataset\\" + "upload_original.csv")
        # specified 4 headers
        keys = df.keys()
        if("o_latitude" not in keys or "o_longitude" not in keys or
            "date_time" not in keys or "weather" not in keys or
                "d_latitude" not in keys or "d_longitude" not in keys):
            # return 1
            raise KeyError(
                "Lack of one or all specified keys, please check date_time, o_latitude, o_longitude, d_latitude, d_longitude, weather.")
        df = df[~df.isnull().any(axis=1)]
        # specified shape without null value
        row_count, column_count = df.shape
        if(row_count < 1024 or column_count != 6):
            # return 1
            raise IndexError(
                "Number of records without null value is less than 1024 or columns count is not 6.")
        # sampling
        df = df.sample(n=1024)
        # sort by timestamp
        df = df.sort_values(by='date_time')
        # encoding rules, hour:0-23, dayofweek:24-30, weather:31-50, o_num&d_num: 51-...
        date_time = to_datetime(df['date_time'], unit='s')
        df['hour'] = date_time.dt.hour
        df['day_of_week'] = date_time.dt.dayofweek + 24
        df['weather'] = df['weather'] + 31
        latitude = df['o_latitude'].append(df['d_latitude'], ignore_index=True)
        longitude = df['o_longitude'].append(
            df['d_longitude'], ignore_index=True)
        min_lat = latitude.min()
        max_lat = latitude.max()
        min_lon = longitude.min()
        max_lon = longitude.max()
        df['o_num'] = df.apply(lambda row: grid_number(
            (row['o_latitude'], row['o_longitude']),
            (min_lat, max_lat), (min_lon, max_lon),
            height, width), axis=1)
        df['d_num'] = df.apply(lambda row: grid_number(
            (row['d_latitude'], row['d_longitude']),
            (min_lat, max_lat), (min_lon, max_lon),
            height, width), axis=1)
        # save to csv
        file_path = '{}\\dataset\\upload_processed.txt'.format(current_dir)
        # with open(file_path, 'a') as f:
        df.to_csv(file_path, sep=' ', columns=[
                  'hour', 'day_of_week', 'weather', 'o_num', 'd_num'], header=False, index=False)
        data_range = {
            'hour': list(df['hour'].unique()),
            'day_of_week': list(df['day_of_week'].unique() - 24),
            'weather': list(df['weather'].unique() - 31),
            'o_num': list(df['o_num'].unique() - 51),
            'd_num': list(df['d_num'].unique() - 51),
        }
        stop = default_timer()
        run_time = stop - start
        results = {
            'date_time': [current_date_time],
            'run_time': [run_time]
        }
        new_row = DataFrame(results)
        file_path = '{}\\try_process_upload_od\\try_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
        return 0, data_range
    except:
        # print(format_exc())
        results = {
            'date_time': current_date_time,
            'exception_info': format_exc()
        }
        # print(results)
        new_row = DataFrame(results, index=[0])
        file_path = '{}\\except_process_upload_od\\except_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
        data_range = {}
        return 1, data_range


# print(process_original_od(10, 10))
