# -*- coding: utf-8 -*-
"""
author = hobin;
email = '627227669@qq.com';
"""


def verifyWeight1(result_sql, sigma=3):
    """
    This assume that the weight of every item is like normal distribution (not standard normal distribution).
    It uses the 3 sigma principle to verify the weight.
    :param result_sql: a list of tuples;
    :return: a tuple which has two values: the lowest value and the highest value
    """
    sum_weight = 0.0
    sum_variance = 0.0
    for index, row in enumerate(result_sql):
        sum_weight = sum_weight + float(row[4])  # assuming the float(row[4]) is the expected number;
        sum_variance = sum_variance + row[5] # assuming the row[5] is the variance of the specific item;
    lowest_weight = sum_weight - sigma*sum_variance**0.5
    highest_weight = sum_weight + sigma*sum_variance**0.5
    return (lowest_weight, highest_weight)


def verifyWeight2(result_sql):
    """
    :param result_sql: a list of tuples
    :return: a tuple which has two values: the lowest value and the highest value
    """
    lowest_weight = 0.0
    highest_weight = 0.0
    for index, row in enumerate(result_sql):
        # assuming the float(row[4]) is the expected number;
        if float(row[4]) < 30:
            lowest_weight = lowest_weight + float(row[4]) * 0.9 
            highest_weight = highest_weight + float(row[4]) * 1.1 
        elif float(row[4]) > 999:
            lowest_weight = lowest_weight + float(row[4]) - 9
            highest_weight = highest_weight + float(row[4]) + 9
        else:
            lowest_weight = lowest_weight + float(row[4]) * 0.95 
            highest_weight = highest_weight + float(row[4]) * 1.05 
    return (lowest_weight, highest_weight)


def verifyWeight2_1(current_weight, result_sql):
    """
    :param current_weight: a float value;
    :param result_sql: a list of tuples;
    :return: Bool
    """
    lowest_weight = 0.0
    highest_weight = 0.0
    for index, row in enumerate(result_sql):
        # assuming the float(row[4]) is the expected number;
        if float(row[4]) < 30:
            lowest_weight = lowest_weight + float(row[4]) * 0.9 
            highest_weight = highest_weight + float(row[4]) * 1.1 
        elif float(row[4]) > 999:
            lowest_weight = lowest_weight + float(row[4]) - 9
            highest_weight = highest_weight + float(row[4]) + 9
        else:
            lowest_weight = lowest_weight + float(row[4]) * 0.95 
            highest_weight = highest_weight + float(row[4]) * 1.05 
    return lowest_weight< current_weight < highest_weight


def verifyWeight2_2(result_sql):
    """
    :param result_sql: a list of tuples
    :return: a tuple which has two values: the lowest value and the highest value
    """
    lowest_weight = 0.0
    highest_weight = 0.0
    for index, row in enumerate(result_sql):
        # assuming the float(row[4]) is the expected number;
        lowest_weight = lowest_weight + float(row[4]) * 0.85
        highest_weight = highest_weight + float(row[4]) * 1.15
    return (lowest_weight, highest_weight)


def verifyWeight3(current_weight, result_sql, group2items,
                  min_ratio = 0.8, max_ratio = 1.2,
                  group_id_index = -2, goods_weight_index = -3):
    """
    :param current_weight: data type is float;
    :param result_sql: a list of tuples; each record should contains the group_id info;
    :param group2items: currently dict data type; key is int and value is a list of tuples;
    :param min_ratio:
    :param max_ratio:
    :return: status_code and sql result;
    """
    sorted_result_sql = []
    # to reduce the calculation, one way is to sort the result based on the group_id;
    for item in result_sql:
        if item[group_id_index]:
            sorted_result_sql.append(item)
        else:
            sorted_result_sql.insert(0, item)
    result_sql = sorted_result_sql

    # print('The sorted sql result based on group_id with length %s:' % len(result_sql))
    # print(result_sql)
    print('The information about group is %s.' % group2items)
    print('The current weight is %s' % current_weight)
    print('------------------------------------------------------------------------')

    # calculating all combinations of detected items;
    all_possible_weight_dict = {'s': 0.0}  # s indicates 'sequence';
    max_weight = current_weight * max_ratio
    for index, item in enumerate(result_sql):
        newest_dict = {}
        item_group_id = item[group_id_index]
        # print('The data type of group id is %s.' % type(item_group_id))
        if item_group_id:
            # the group id is not None;
            group_info = group2items.get(item_group_id) # I am afraid there is no item information under the specific group id;
            if group_info:
                # the group id exists and corresponding information exists;
                for selection_index, one_item_record in enumerate(group_info):
                    selection_index_str = str(selection_index)
                    weight_increment = float(one_item_record[goods_weight_index])
                    for key in list(all_possible_weight_dict.keys()):
                        new_key = key + selection_index_str
                        # Be careful! the information stored in the last iteration dictionary should not be deleted;
                        # 1, save the possibility directly
                        # all_possible_weight_dict[new_key] = all_possible_weight_dict.pop(key) + weight_increment  # incorrect
                        # newest_dict[new_key] = all_possible_weight_dict[key] + weight_increment

                        # 2, reduce some possibility
                        new_key_weight = all_possible_weight_dict[key] + weight_increment
                        if new_key_weight < max_weight:
                            newest_dict[new_key] = new_key_weight
                all_possible_weight_dict = newest_dict
            else:
                # the group id exists but there is no corresponding information;
                weight_increment = float(item[goods_weight_index])
                for key in list(all_possible_weight_dict.keys()):
                    new_key = key + 'E'  # do not append 0 to the sequence of key since 0,1,2... are used when the group id is not None;
                    # Be careful! the information stored in the last iteration dictionary should not be deleted;
                    # 1, save the possibility directly
                    # all_possible_weight_dict[new_key] = all_possible_weight_dict.pop(key) + weight_increment  # incorrect
                    # newest_dict[new_key] = all_possible_weight_dict[key] + weight_increment

                    # 2, reduce some possibility
                    new_key_weight = all_possible_weight_dict[key] + weight_increment
                    if new_key_weight < max_weight:
                        newest_dict[new_key] = new_key_weight
                all_possible_weight_dict = newest_dict
        else:
            # the group id is None;
            weight_increment = float(item[goods_weight_index])
            for key in list(all_possible_weight_dict.keys()):
                new_key = key + 'N'  # do not append 0 to the sequence of key since 0,1,2... are used when the group id is not None;
                # Be careful! the information stored in the last iteration dictionary should not be deleted;
                # 1, save the possibility directly
                # all_possible_weight_dict[new_key] = all_possible_weight_dict.pop(key) + weight_increment  # incorrect
                # newest_dict[new_key] = all_possible_weight_dict[key] + weight_increment

                # 2, reduce some possibility
                new_key_weight = all_possible_weight_dict[key] + weight_increment
                if new_key_weight < max_weight:
                    newest_dict[new_key] = new_key_weight
            all_possible_weight_dict = newest_dict

        # The print statement below might raise error 'OSError: [Errno 22] Invalid argument' when there is 3**50 possibility.
        # print('The current possible combination with index %s is %s.' % (index, all_possible_weight_dict))
        # print('The current index is %s' % index)
        # print('------------------------------------------------------------------------')

    # finding the optimized value;
    in_range_counter = 0
    optimized_key = 's'
    optimized_distance = current_weight
    if len(all_possible_weight_dict) > 0:
        min_weight = current_weight * min_ratio
        max_weight = current_weight * max_ratio
        for key, weight_value in all_possible_weight_dict.items():
            new_distance = abs(weight_value - current_weight)
            if min_weight < weight_value < max_weight:
                if in_range_counter == 0:
                    optimized_distance = new_distance
                    optimized_key = key
                elif optimized_distance > new_distance:
                    optimized_distance = new_distance
                    optimized_key = key
                in_range_counter = in_range_counter + 1
        print('The optimized key is %s.' % optimized_key)
        print('------------------------------------------------------------------------')
    else:
        print('There is no optimized key.')
        print('------------------------------------------------------------------------')

    # restoring the final result of sql;
    final_result_sql = []
    status_code = '2'  # assuming that algorithm error happens
    if in_range_counter == 0:
        final_result_sql = result_sql  # Why is it not an empty list? My workmate need to know the result detected by model;
        status_code = '1'
        print('All combination of detected items do not pass the weight verification.')
    else:
        print('The optimized key passes the weight verification.')
        if len(optimized_key) == len(result_sql) + 1:
            for index, char in enumerate(optimized_key[1:]):
                if char == 'N' or char == 'E':
                    final_result_sql.append(result_sql[index])
                else:
                    item_group_id = result_sql[index][group_id_index]
                    final_result_sql.append(group2items[item_group_id][int(char)])
            status_code = '0'
            print('The final result is %s.' % final_result_sql)
            print('The optimized distance is %s.' % optimized_distance)
        else:
            final_result_sql = result_sql  # Why is it not an empty list? My workmate need to know the result detected by model;
            status_code = '2'
            print('Algorithm error happens')

    return status_code, final_result_sql

if __name__ == '__main__':
    result_sql = [
        ('a','b','c','d','10'),
        ('a','b','c','d','12')
    ]
    a = verifyWeight2_1(22, result_sql)
    print(a)

