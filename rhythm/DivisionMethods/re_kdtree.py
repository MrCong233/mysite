#!python numbers=disable

# Copyleft 2008 Sturla Molden
# University of Oslo

# import psyco
# psyco.full()
import numpy as np
import pandas as pd
import json
import os.path as pwd
import psycopg2
import timeit
import glob
import ntpath


def kdtree(data, divide_depth=1):
    """
    build a kd-tree for O(n log n) nearest neighbour search

    input:
        data:       2D ndarray, shape =(ndim,ndata), preferentially C order
        leafsize:   max. number of data points to leave in a leaf

    output:
        kd-tree:    list of tuples
    """

    ndim = data.shape[0]
    ndata = data.shape[1]

    # find bounding hyper-rectangle
    hrect = np.zeros((2, data.shape[0]))
    hrect[0, :] = data.min(axis=1)
    hrect[1, :] = data.max(axis=1)

    # create root of kd-tree
    idx = np.argsort(data[0, :], kind='mergesort')
    data[:, :] = data[:, idx]
    splitval = data[0, int(ndata/2)]

    left_hrect = hrect.copy()
    right_hrect = hrect.copy()
    left_hrect[1, 0] = splitval
    right_hrect[0, 0] = splitval

    # idx, data, left_hrect, right_hrect, left_nodeptr, right_nodeptr, current_level_hrect
    tree = [(None, None, left_hrect, right_hrect, None, None, hrect)]
    # data, idx, depth, parent, leftbranch
    stack = [(data[:, :int(ndata/2)], idx[:int(ndata/2)], 1, 0, True),
             (data[:, int(ndata/2):], idx[int(ndata/2):], 1, 0, False)]

    # recursively split data in halves using hyper-rectangles:
    while stack:

        # pop data off stack
        data, didx, depth, parent, leftbranch = stack.pop()
        ndata = data.shape[1]
        nodeptr = len(tree)

        # update parent node

        _didx, _data, _left_hrect, _right_hrect, left, right, _current_level_hrect = tree[
            parent]

        tree[parent] = (_didx, _data, _left_hrect, _right_hrect, nodeptr, right, _current_level_hrect) if leftbranch \
            else (_didx, _data, _left_hrect, _right_hrect, left, nodeptr, _current_level_hrect)

        if leftbranch:
            current_level_hrect = _left_hrect
        else:
            current_level_hrect = _right_hrect

        # insert node in kd-tree

        # leaf node?
        if depth >= divide_depth:
            # if ndata <= leafsize:
            _didx = didx.copy()
            _data = data.copy()
            # leaf = (_didx, _data, None, None, 0, 0)
            leaf = (_didx, _data, None, None, -1, -1, current_level_hrect)
            tree.append(leaf)

        # not a leaf, split the data in two
        else:
            splitdim = depth % ndim
            idx = np.argsort(data[splitdim, :], kind='mergesort')
            data[:, :] = data[:, idx]
            didx = didx[idx]
            nodeptr = len(tree)
            stack.append(
                (data[:, :int(ndata/2)], didx[:int(ndata/2)], depth+1, nodeptr, True))
            stack.append(
                (data[:, int(ndata/2):], didx[int(ndata/2):], depth+1, nodeptr, False))
            splitval = data[splitdim, int(ndata/2)]
            if leftbranch:
                left_hrect = _left_hrect.copy()
                right_hrect = _left_hrect.copy()
            else:
                left_hrect = _right_hrect.copy()
                right_hrect = _right_hrect.copy()
            left_hrect[1, splitdim] = splitval
            right_hrect[0, splitdim] = splitval
            # append node to tree
            tree.append((None, None, left_hrect, right_hrect,
                         None, None, current_level_hrect))

    return tree


def part_index_using_hrect(tuples_list_, latitude_, longitude_):
    for idx in range(len(tuples_list_)):
        hrect_ = tuples_list_[idx][6]
        if latitude_ >= hrect_[0, 0] and latitude_ <= hrect_[1, 0]:
            if longitude_ >= hrect_[0, 1] and longitude_ <= hrect_[1, 1]:
                return idx
    return -1


def count_in_or_between_parts_using_kdtree(records, date_, start_hour_, end_hour_, divide_depth_):
    records_nparray = np.reshape(np.asarray(records), (-1, 2)).T
    tree_tuples_list = kdtree(records_nparray, divide_depth_)
    leaf_tuples_list = [
        item for item in tree_tuples_list if item[4] == -1 and item[5] == -1]
    not_leaf_tuples_list = [
        {"hrect": item[6].tolist(), "left_nodeptr": item[4], "right_nodeptr": item[5]} for item in tree_tuples_list]
    part_idx_gps = []
    for idx in range(len(leaf_tuples_list)):
        _data = leaf_tuples_list[idx][1]
        _ndata = _data.shape[1]
        single_part = (_data[0, int(_ndata / 2)],
                       _data[1, int(_ndata / 2)])
        part_idx_gps.append(single_part)
    sum_matrix = np.zeros(
        (len(part_idx_gps), len(part_idx_gps)), dtype=np.int)
    for i in range(len(records)):
        idx_up = part_index_using_hrect(
            leaf_tuples_list, records[i][0], records[i][1])
        idx_off = part_index_using_hrect(
            leaf_tuples_list, records[i][2], records[i][3])
        if idx_up >= 0 and idx_off >= 0:
            sum_matrix[idx_up, idx_off] += 1
    sum_matrix_list = sum_matrix.tolist()
    dataset_hour_json_of_all = "{}_h{}_{}_dd{}.json".format(
        date_, start_hour_, end_hour_, divide_depth_)
    json_of_all = {
        "kd_tree_not_leaf_node": not_leaf_tuples_list,
        "idx_gps": part_idx_gps,
        "sum_matrix": sum_matrix_list
    }
    dirname_ = pwd.dirname(__file__)
    with open(dirname_ + "\\dataset\\" + dataset_hour_json_of_all, 'w') as outfile:
        json.dump(json_of_all, outfile)


def count_in_or_between_parts_using_db(date_, start_hour_, end_hour_):
    """
    date_: a date format like 2014-08-03
    start_hour_: a format of hour like [0, 23]
    end_hour_: a format of hour
    divide_depth_: an integer like [1, 8]
    """
    sql_of_select_od_pairs = "SELECT origin_latitude, origin_longitude, destination_latitude, destination_longitude\
                                FROM (\
	                            SELECT \
                                    taxi_id,\
                                    latitude AS origin_latitude, longitude AS origin_longitude, \
                                    LEAD(latitude, 1) OVER (PARTITION BY taxi_id ORDER BY date_time) AS destination_latitude, \
                                    LEAD(longitude, 1) OVER (PARTITION BY taxi_id ORDER BY date_time) AS destination_longitude, \
                                    origin, LEAD(origin, 1) OVER (PARTITION BY taxi_id ORDER BY date_time) AS destination,\
                                    date_time\
                                FROM (\
                                    SELECT taxi_id, latitude, longitude, (passenger = TRUE) AS origin, date_time\
                                    FROM (\
                                        SELECT *\
                                        FROM (\
                                            SELECT taxi_id, latitude, longitude, passenger, LAG(passenger, 1) OVER (PARTITION BY taxi_id ORDER BY date_time) AS last_passenger, date_time\
                                            FROM  (\
                                                SELECT *\
                                                FROM _{}\
                                                WHERE date_time >= timestamp '{} {}:00:00' AND date_time < timestamp '{} {}:00:00'\
                                            ) AS temp\
                                        ) AS temp\
                                        WHERE passenger != last_passenger\
                                    ) AS temp\
                                ) AS temp\
                            ) AS temp\
                            WHERE origin = TRUE AND destination = FALSE;".format(date_.replace('-', ''), date_, start_hour_, date_, end_hour_)
    # print(sql_of_select_od_pairs)
    try:
        connection = psycopg2.connect(user="postgres",
                                      password="StephenHao@3023",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="urban_cross_domain_data"
                                      )
        cursor = connection.cursor()
        # start_sql = timeit.default_timer()
        cursor.execute(sql_of_select_od_pairs)
        # end_sql = timeit.default_timer()
        # print('time: ', end_sql - start_sql)
        records = cursor.fetchall()
        if records:
            # return records
            for i in range(8):
                count_in_or_between_parts_using_kdtree(
                    records, date_, start_hour_, end_hour_, i+1)
    except (psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL: ", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")


def load_json_of_one_hour_result(date_, start_hour_, end_hour_, divide_depth_):
    dirname_ = pwd.dirname(__file__)
    json_directory_path = dirname_ + "\\dataset\\"
    json_path = json_directory_path + \
        "{}_h{}_{}_dd{}.json".format(
            date_, start_hour_, end_hour_, divide_depth_)
    with open(json_path) as input_:
        json_ = json.load(input_)
    return json_


def generate_all_json():
    file_paths = glob.glob(
        r"E:\acer\VSProjects\mysite\rhythm\algorithm\dataset\*.txt")
    for single_file_path in file_paths:
        single_file_name = ntpath.basename(single_file_path)
        file_name_list = single_file_name.split('_')
        if file_name_list[-1] == "train.txt":
            year = file_name_list[0][0:4]
            month = file_name_list[0][4:6]
            day = file_name_list[0][6:8]
            if day in ["24", "25", "26", "27", "28", "29", "30"]:
                for i in range(6, 24):
                    start = timeit.default_timer()
                    count_in_or_between_parts_using_db(
                        "{}-{}-{}".format(year, month, day), i, i + 1)
                    end = timeit.default_timer()
                    print("{}-{}-{} {}--{}: ".format(year,
                                                     month, day, i, i + 1), end - start)
