import os.path
from csv import reader, writer
from itertools import permutations
# import time
# import argparse
# import numpy as np
# import matplotlib.pyplot as plt
#-----------------------------#
from eclat import eclat
# from .eclat import eclat
#-----------------------#


def read_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # no headers in upload_preprocessed.txt
    data_path = current_dir + '\\dataset\\upload_processed.txt'
    data = []
    with open(data_path, 'r') as f:
        file = reader(f, delimiter=' ', quotechar='\r')
        for row in file:
            data.append(row)
    return data


def write_result(result):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    result_path = current_dir + '\\dataset\\upload_mined.txt'
    with open(result_path, 'w') as file:
        file_data = writer(file, delimiter=',', quotechar='\r')
        for itemset_K in result[0]:
            for itemset in itemset_K:
                output_string = ''
                for item in itemset:
                    output_string += str(item)+' '
                output_string += '(' + str(result[1][itemset]) + ')'
                file_data.writerow([output_string])


def frequent_itemset_mining(min_support):
    data = read_data()
    result = eclat(data, min_support=min_support, iterative=False,
                   use_CUDA=False, block=16, thread=16)
    itemsets = result
    if len(itemsets) == 0:
        # 'Found 0 frequent itemset, please try again with a lower minimum support value!'
        return 1, itemsets
    # write_result(result)
    return 0, itemsets


def rules(FreqItems, confidence):
    Rules = []
    cnt = 0
    for items, support in FreqItems.items():
        items_len = len(items)
        if (items_len > 1):
            all_perms = list(permutations(items, items_len))
            for lst in all_perms:
                for conseq_len in range(1, items_len):
                    antecedent = lst[:items_len - conseq_len]
                    consequent = lst[-conseq_len:]
                    if antecedent in FreqItems and consequent in FreqItems:
                        conf = FreqItems[items] / FreqItems[antecedent]
                        if conf >= confidence:
                            cnt += 1
                            Rules.append(
                                (antecedent, consequent, support, conf))
    return cnt, Rules


# rtn, items = frequent_itemset_mining(0.02)
# print(rtn, items)
# print(rules(items[1], 0.5))
