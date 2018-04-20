# -*- coding: utf-8 -*-
"""

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


if __name__ == '__main__':
    result_sql = [
        ('a','b','c','d','10'),
        ('a','b','c','d','12')
    ]
    a = verifyWeight2_1(22, result_sql)
    print(a)

