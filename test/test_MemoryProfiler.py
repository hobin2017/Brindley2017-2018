# -*- coding: utf-8 -*-
"""

"""
from memory_profiler import profile
# 1, analyse the memory usage line-by-line
@profile(precision=4)  # if precision =4, then memory usage 48M will be 48.0000M.
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a

if __name__ == '__main__':
    counter = 5
    while counter > 0:
        my_func()
        counter = counter - 1


