import os.path
from timeit import default_timer
from traceback import format_exc
from datetime import datetime
from pandas import read_csv, to_datetime, DataFrame
from numpy import int64


def process_original_csv(token):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        start = default_timer()
        df = read_csv(current_dir + "\\dataset\\" +
                      "upload_original-{}.csv".format(token))
        # specified 3 headers
        keys = df.keys()
        if("latitude" not in keys or "longitude" not in keys or "date_time" not in keys):
            # return 1
            raise KeyError(
                "Lack of one or all specified keys, please check latitude, longitude, date_time.")
        df = df[~df.isnull().any(axis=1)]
        # specified shape without null value
        row_count, column_count = df.shape
        if(row_count < 1024 or column_count != 3):
            # return 1
            raise IndexError(
                "Number of records without null value is less than 1024 or columns count is not 3.")
        # sampling
        df = df.sample(n=1024)

        # specified date_time format
        # date_time_format = "%Y-%m-%d %H:%M:%S"
        # formated = to_datetime(
        #     df['date_time'], format=date_time_format, errors='raise')
        # if formated.notnull().all() == True:
        # return 1
        # raise TypeError(
        #     "Type of \"data_time\" must be \"%Y-%m-%d %H:%M:%S\"")
        # date_time format convert to unix timestamp
        # df['date_time'] = df['date_time'].values.astype(int64) // 10 ** 9

        # sort by timestamp
        df = df.sort_values(by='date_time')
        # save to csv
        file_path = '{}\\dataset\\upload_processed-{}.csv'.format(
            current_dir, token)
        # with open(file_path, 'a') as f:
        df.to_csv(file_path, header=False, index=False)
        stop = default_timer()
        run_time = stop - start
        results = {
            'date_time': current_date_time,
            'run_time': run_time,
            'token': token
        }
        new_row = DataFrame(results, index=[0])
        file_path = '{}\\try_process_upload_original\\try_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
        return 0
    except:
        # print(format_exc())
        results = {
            'date_time': current_date_time,
            'exception_info': format_exc(),
            'token': token
        }
        # print(results)
        new_row = DataFrame(results, index=[0])
        file_path = '{}\\except_process_upload_original\\except_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
        return 1


# print(process_original_csv())
