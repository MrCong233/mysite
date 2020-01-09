import re_gui21
import timeit
import traceback
import json


def test_space_time_or_time_space(method, arg1_start, arg1_end, arg2_start, arg2_end):
    results = dict()
    for i in range(arg1_start, arg1_end):
        for j in range(arg2_start, arg2_end):
            try:
                start = timeit.default_timer()
                _, extra = re_gui21.figure_to_img(
                    "data1024", method, [i, j], True)
                stop = timeit.default_timer()
                run_time = stop - start
                if len(extra) != 0:
                    info = 1
                else:
                    info = 0
                results["{},{}".format(i, j)] = (run_time, info)
            except:
                results["{},{}".format(i, j)] = traceback.format_exc()
    with open('test_re_gui21_result/test_{}_result.json'.format(method), 'w') as fp:
        json.dump(results, fp)
    print(results)


def test_head_5_methods(method, arg_start, arg_end):
    results = dict()
    for i in range(arg_start, arg_end):
        try:
            start = timeit.default_timer()
            _, extra = re_gui21.figure_to_img(
                "data1024", method, [i], True)
            stop = timeit.default_timer()
            run_time = stop - start
            if len(extra) != 0:
                info = 1
            else:
                info = 0
            results["{}".format(i)] = (run_time, info)
        except:
            results["{}".format(i)] = traceback.format_exc()
    with open('test_re_gui21_result/test_{}_result.json'.format(method), 'w') as fp:
        json.dump(results, fp)
    print(results)


# test_space_time_or_time_space("space_time", 9, 11, 1, 12)
# test_space_time_or_time_space("space_time", 1, 12, 1, 12)
# test_space_time_or_time_space("time_space", 2, 12, 1, 12)
# test_head_5_methods("3d_slice_merge", 1, 12)
# test_head_5_methods("3d_kdtree", 1, 12)
# test_head_5_methods("3d_equal_grid", 1, 12)
# test_head_5_methods("2d_kdtree", 1, 12)
# test_head_5_methods("2d_equal_grid", 1, 12)
