from . import re_gui21
# import re_gui21
import os.path
from timeit import default_timer
from traceback import format_exc
from datetime import datetime
from pandas import DataFrame


def interface_to_generate_img(file_name, token, method, args, test_or_not):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # print("*", current_dir)
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        start = default_timer()
        file_name += "-{}".format(token)
        img_address, extra = re_gui21.figure_to_img(
            file_name, method, args, test_or_not)
        stop = default_timer()
        run_time = stop - start
        if len(extra) != 0:
            info = 1
        else:
            info = 0
        results = {
            'date_time': current_date_time,
            'method': method,
            'args': [args],
            'run_time': run_time,
            'info': info
        }
        new_row = DataFrame(results)
        file_path = '{}\\try_interface_to_methods\\try_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
    except:
        img_address = ""
        extra = {}
        results = {
            'date_time': current_date_time,
            'method': method,
            'args': [args],
            'exception_info': format_exc()
        }
        new_row = DataFrame(results)
        # print(new_row)
        file_path = '{}\\except_interface_to_methods\\except_{}.csv'.format(
            current_dir, current_date)
        with open(file_path, 'a') as f:
            new_row.to_csv(f, header=False, index=False)
    # print(results)
    return img_address, extra


# print(interface_to_generate_img("upload_processed",
    # '3c64618aec575b7c36d5a08d86949c14', "2d_equal_grid", [2], False))
# interface_to_generate_img("upload_processed",
#                           '3c64618aec575b7c36d5a08d86949c14', "time_space", [1, 2], True)
# print(interface_to_generate_img("upload_processed",
#                                 '3c64618aec575b7c36d5a08d86949c14', "time_space", [2, 2], True))
# interface_to_generate_img("data1024", "space_time", [2, 2], True)
# interface_to_generate_img("data1024", "space_time", [2, 2], False)
