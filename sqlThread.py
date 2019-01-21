"""
Thread for SQL statements
author = hobin;
email = '627227669@qq.com';
"""
from collections import Counter

import mysql.connector
import logging

import time
from PyQt5.QtCore import QThread, pyqtSignal
from memory_profiler import profile


class MyThread3(QThread):
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyThread3, self).__init__(parent)
        self.parent = parent
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        self.conn = mysql.connector.connect(user='root', password='qwerQWER', database='hobin')
        print('Connection to database is successful')


    def run(self):
        print('SQL thread (begin): %s'% self.detected_result)
        results = []
        if len(self.detected_result)>=0:
            cursor = self.conn.cursor()
            for i in self.detected_result:
                cursor.execute('select goods_name, goods_spec, sku_price, sku_id from storegoods where cv_id = %s', (i,))
                results = results + cursor.fetchall()
            print('SQL thread (end): %s'% results)
            cursor.close()
            self.finished.emit(results)


class MyThread3_1(QThread):
    """
    Compared with the MyThread3 class, the logging module is introduced to this module at first time.
    """
    finished = pyqtSignal(object)

    def __init__(self, parent=None, logger_name='hobin', *, db_user= 'root', db_pass='qwerQWER', db_database='hobin',
                 db_port='3306', db_host = '127.0.0.1',  **kwargs):
        """
        :param parent:
        :param db_user:
        :param db_pass:
        :param db_database:
        :param db_port: be sure that it is an integer
        :param db_host:
        :param logger_name:
        :param kwargs:
        """
        super(MyThread3_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.conn = mysql.connector.connect(user= db_user, password=db_pass, database=db_database, port=int(db_port), host=db_host)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.conn = mysql.connector.connect(user=kwargs['db_user'], password=kwargs['db_pass'], database=kwargs['db_database'],
        #                                     port=int(kwargs['db_port']), host=kwargs['db_host'])

        # some variables
        self.mylogger3_1 = logging.getLogger(logger_name)
        self.parent = parent
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        # print('Connection to database is successful')
        self.mylogger3_1.info('Connection to database is successful')


    def run(self):
        # print('SQL Thread (begin): %s'% self.detected_result)
        self.mylogger3_1.debug('SQL thread (begin): %s'% self.detected_result)
        results = []
        if len(self.detected_result)>=0:
            cursor = self.conn.cursor()
            for i in self.detected_result:
                cursor.execute('select goods_name, goods_spec, sku_price, sku_id from storegoods where cv_id = %s', (i,))
                results = results + cursor.fetchall()
            # print('SQL result (end): %s'% results)
            self.mylogger3_1.debug('SQL thread (end): %s'% results)
            cursor.close()
            self.finished.emit(results)


class MyThread3_2(QThread):
    """
    Compared with the MyThread3 class, this class only get access to mysql database once over the run() function.
    The main idea is using the order of the cv_id to do the alignment (sql 'order by' and 'sorted(Counter.keys())').
    """
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyThread3_2, self).__init__(parent)
        self.parent = parent
        self.sql_command_start = 'select goods_name, goods_spec, sku_price, sku_id from storegoods where cv_id in '
        self.sql_tuple = ()
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        self.conn = mysql.connector.connect(user='root', password='commaai2017', database='hobin')
        print('Connection to database is successful')

    #@profile(precision=2)
    def run(self):
        print('SQL thread (begin): %s'% self.detected_result)
        if len(self.detected_result)>=0:
            # 1, the configuration of sql command and sql tuple for cursor.execute()
            result_reduced = Counter(self.detected_result)
            # print(result_reduced)
            sql_command_end = '('
            for _ in range(len(result_reduced)):
                sql_command_end = sql_command_end + '%s,'
            sql_command_end = sql_command_end[:-1] + ') order by cv_id'  # deleting the last comment - comma.
            # print(sql_command_end)
            self.sql_tuple = tuple(result_reduced)  # changing the dictionary type to the tuple type as cursor.execute() requires.
            # print(self.sql_tuple)

            # 2, the execution of the sql querying
            cursor = self.conn.cursor()
            cursor.execute(self.sql_command_start + sql_command_end, self.sql_tuple)
            results_init = cursor.fetchall()  # a list of tuples
            # print('the initial SQL results are: %s'%results_init)

            # 3, restoring the correct result
            results_final = []
            if len(result_reduced) < len(self.detected_result):
                result_reduced_sorted = sorted(result_reduced.keys())
                # print('the reduced and sorted result is %s' %result_reduced_sorted)
                for index, key in enumerate(result_reduced_sorted):
                    for _ in range(result_reduced[key]):
                        results_final.append(results_init[index])
            else:
                results_final = results_init
            # 4, the end
            print('SQL thread (end): %s'% results_final)
            cursor.close()
            self.finished.emit(results_final)


class MyThread3_2_1(QThread):
    """
    Compared with the MyThread3 class, this class only get access to mysql database once over the run() function.
    Compared with the MyThread3_2 class, the logging module is introduced to this module at first time.
    Compared with the MyThread3_2 class, try...except statement is added to prevent the connection to database is closed.
    Compared with the MyThread3_2 class, the information of the goods_weight is also retrieved from the database.
    """
    finished = pyqtSignal(object)
    error_connection = pyqtSignal()
    error_algorithm = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, db_user= 'root', db_pass='qwerQWER', db_database='hobin',
                 db_port='3306', db_host = '127.0.0.1',  **kwargs):
        """
        :param parent:
        :param db_user:
        :param db_pass:
        :param db_database:
        :param db_port: be sure that it is an integer
        :param db_host:
        :param logger_name:
        :param kwargs:
        """
        super(MyThread3_2_1, self).__init__(parent)
        self.mysql_config = {
            'user': db_user,
            'password': db_pass,
            'port': int(db_port),
            'host': db_host,
            'database': db_database
        }
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.conn = mysql.connector.connect(**self.mysql_config)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.conn = mysql.connector.connect(user=kwargs['db_user'], password=kwargs['db_pass'], database=kwargs['db_database'],
        #                                     port=int(kwargs['db_port']), host=kwargs['db_host'])

        # some variables
        self.mylogger3_2_1 = logging.getLogger(logger_name)
        self.parent = parent
        self.sql_command_start = 'select goods_name, goods_spec, sku_price, sku_id, goods_weight from storegoods where cv_id in '
        self.sql_tuple = ()
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        # print('Connection to database is successful')
        self.mylogger3_2_1.info('Connection to database is successful')


    def run(self):
        # print('SQL thread (begin): %s'% self.detected_result)
        self.mylogger3_2_1.debug('SQL thread (begin): %s'% self.detected_result)
        if len(self.detected_result)>0:
            # 1, the configuration of sql command and sql tuple for cursor.execute()
            result_reduced = Counter(self.detected_result)
            # print(result_reduced)
            sql_command_end = '('
            for _ in range(len(result_reduced)):
                sql_command_end = sql_command_end + '%s,'
            sql_command_end = sql_command_end[:-1] + ') order by cv_id'  # deleting the last comment - comma.
            # print(sql_command_end)
            self.sql_tuple = tuple(result_reduced)  # changing the dictionary type to the tuple type as cursor.execute() requires.
            # print(self.sql_tuple)

            # 2, the execution of the sql querying
            try:
                cursor = self.conn.cursor()
                cursor.execute(self.sql_command_start + sql_command_end, self.sql_tuple)
                results_init = cursor.fetchall()  # a list of tuples
                # print('the initial SQL results are: %s'%results_init)

                # 3, restoring the correct result
                results_final = []
                if len(result_reduced) < len(self.detected_result):
                    result_reduced_sorted = sorted(result_reduced.keys())
                    # print('the reduced and sorted result is %s' %result_reduced_sorted)
                    for index, key in enumerate(result_reduced_sorted):
                        for _ in range(result_reduced[key]):
                            results_final.append(results_init[index])
                else:
                    results_final = results_init
                # 4, the end
                # print('SQL thread (end): %s'% results_final)
                self.mylogger3_2_1.debug('SQL thread (end): %s' % results_final)
                cursor.close()
                self.finished.emit(results_final)
            except mysql.connector.Error as e:
                # self.mylogger3_2_1.error(e)
                self.mylogger3_2_1.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
                self.conn.close()
                self.conn = mysql.connector.connect(**self.mysql_config)
                self.error_connection.emit()
            except BaseException:
                self.mylogger3_2_1.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
                self.error_algorithm.emit()
        else:
            self.finished.emit([])


class MyThread3_2_2(QThread):
    """
    Compared with the MyThread3 class, this class only get access to mysql database once over the run() function.
    Compared with the MyThread3_2 class, the logging module is introduced to this module at first time.
    Compared with the MyThread3_2 class, try...except statement is added to prevent the connection to database is closed.
    Compared with the MyThread3_2 class, the information of the goods_weight is also retrieved from the database.
    Compared with the MyThread3_2_1 class, this class improve the stability of the algorithm since the database does not have the corresponding record;
    the sql command also needs to be changed to keep the cv_id for every record (keeping cv_id as the last one!);
    """
    finished = pyqtSignal(object)
    error_connection = pyqtSignal()
    error_algorithm = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, db_user= 'root', db_pass='qwerQWER', db_database='hobin',
                 db_port='3306', db_host = '127.0.0.1',  **kwargs):
        """
        :param parent:
        :param db_user:
        :param db_pass:
        :param db_database:
        :param db_port: be sure that it is an integer
        :param db_host:
        :param logger_name:
        :param kwargs:
        """
        super(MyThread3_2_2, self).__init__(parent)
        self.mysql_config = {
            'user': db_user,
            'password': db_pass,
            'port': int(db_port),
            'host': db_host,
            'database': db_database
        }
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.conn = mysql.connector.connect(**self.mysql_config)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.conn = mysql.connector.connect(user=kwargs['db_user'], password=kwargs['db_pass'], database=kwargs['db_database'],
        #                                     port=int(kwargs['db_port']), host=kwargs['db_host'])

        # some variables
        self.mylogger3_2_2 = logging.getLogger(logger_name)
        self.parent = parent
        self.sql_command_start = 'select goods_name, goods_spec, sku_price, sku_id, goods_weight, cv_id from storegoods where cv_id in '
        self.sql_tuple = ()
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        # print('Connection to database is successful')
        self.mylogger3_2_2.info('Connection to database is successful')


    def run(self):
        # print('SQL thread (begin): %s'% self.detected_result)
        self.mylogger3_2_2.debug('SQL thread (begin): %s'% self.detected_result)
        if len(self.detected_result)>0:
            # 1, the configuration of sql command and sql tuple for cursor.execute()
            result_reduced = Counter(self.detected_result)
            # print(result_reduced)
            sql_command_end = '('
            for _ in range(len(result_reduced)):
                sql_command_end = sql_command_end + '%s,'
            sql_command_end = sql_command_end[:-1] + ') order by cv_id'  # deleting the last comment - comma.
            # print(sql_command_end)
            self.sql_tuple = tuple(result_reduced)  # changing the dictionary type to the tuple type as cursor.execute() requires.
            # print(self.sql_tuple)

            # 2, the execution of the sql querying
            try:
                cursor = self.conn.cursor()
                cursor.execute(self.sql_command_start + sql_command_end, self.sql_tuple)
                results_init = cursor.fetchall()  # a list of tuples
                # print('the initial SQL results are: %s'%results_init)

                # 3, restoring the correct result
                results_final = []
                if len(result_reduced) < len(self.detected_result):
                    if len(results_init) == len(result_reduced):
                        result_reduced_sorted = sorted(result_reduced.keys())
                        # print('the reduced and sorted result is %s' %result_reduced_sorted)
                        for index, key in enumerate(result_reduced_sorted):
                            for _ in range(result_reduced[key]):
                                results_final.append(results_init[index])
                    else:
                        # the database might has no record for some cv_id;
                        self.mylogger3_2_2.debug('SQL thread: some records do not exist in the database and the initial result with length %s is %s.'
                                                %(len(results_init), results_init))
                        reserved_key_list = []
                        for record_line in results_init:
                            # by default, the results_init
                            # by default, the last element is the cv_id and the data type is int;
                            reserved_key_list.append(str(record_line[-1]))
                        # self.mylogger3_2_2.debug('SQL thread: %s' % reserved_key_list)
                        # you must convert the str type back to the int type before sorting since the data type is int in database;
                        # Otherwise, the index of results_init[index] used in restoring the details, will cause the incorrect result;
                        result_double_reduced = {}
                        for reserved_key in reserved_key_list:
                            if result_reduced.get(reserved_key):
                                result_double_reduced[int(reserved_key)] = result_reduced.get(reserved_key)
                        self.mylogger3_2_2.debug('SQL thread: %s' %result_double_reduced)
                        # restoring the details
                        result_double_reduced_sorted = sorted(result_double_reduced.keys())
                        for index, key in enumerate(result_double_reduced_sorted):
                            for _ in range(result_double_reduced[key]):
                                results_final.append(results_init[index])

                else:
                    results_final = results_init
                # 4, the end
                # print('SQL thread (end): %s'% results_final)
                self.mylogger3_2_2.debug('SQL thread (end): %s' % results_final)
                cursor.close()
                self.finished.emit(results_final)
            except mysql.connector.Error as e:
                # self.mylogger3_2_2.error(e)
                self.mylogger3_2_2.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
                self.conn.close()
                self.conn = mysql.connector.connect(**self.mysql_config)
                self.error_connection.emit()
            except BaseException:
                self.mylogger3_2_2.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
                self.error_algorithm.emit()
        else:
            self.finished.emit([])


class MyThread3_2_3(QThread):
    """
    Compared with the MyThread3_2_2 class, this class gets access to the database multiple times just like the MyThread3 class.
    Compared with the MyThread3_2_2 class, this class establish the new connection to the database every time since there is a cache for every connection;
    """
    finished = pyqtSignal(object)
    error_connection = pyqtSignal()
    error_algorithm = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, db_user= 'root', db_pass='qwerQWER', db_database='hobin',
                 db_port='3306', db_host = '127.0.0.1',  **kwargs):
        """
        :param parent:
        :param db_user:
        :param db_pass:
        :param db_database:
        :param db_port: be sure that it is an integer
        :param db_host:
        :param logger_name:
        :param kwargs:
        """
        super(MyThread3_2_3, self).__init__(parent)
        self.mysql_config = {
            'user': db_user,
            'password': db_pass,
            'port': int(db_port),
            'host': db_host,
            'database': db_database
        }
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.conn = mysql.connector.connect(**self.mysql_config)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.conn = mysql.connector.connect(user=kwargs['db_user'], password=kwargs['db_pass'], database=kwargs['db_database'],
        #                                     port=int(kwargs['db_port']), host=kwargs['db_host'])

        # some variables
        self.mylogger3_2_3 = logging.getLogger(logger_name)
        self.parent = parent
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        # print('Connection to database is successful')
        self.mylogger3_2_3.info('Connection to database is successful')


    def run(self):
        self.mylogger3_2_3.debug('SQL thread (begin): %s'% self.detected_result)
        if len(self.detected_result)>0:
            try:
                self.conn = mysql.connector.connect(**self.mysql_config)
                results = []
                cursor = self.conn.cursor()
                for i in self.detected_result:
                    cursor.execute('select goods_name, goods_spec, sku_price, sku_id, goods_weight, cv_id from storegoods where cv_id = %s', (i,))
                    results = results + cursor.fetchall()
                cursor.close()
                self.mylogger3_2_3.debug('SQL thread (end): %s' % results)
                self.conn.close()
                self.finished.emit(results)
            except mysql.connector.Error as e:
                # self.mylogger3_2_3.error(e)
                self.mylogger3_2_3.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
                self.conn.close()
                self.conn = mysql.connector.connect(**self.mysql_config)
                self.error_connection.emit()
            except BaseException:
                self.mylogger3_2_3.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
                self.error_algorithm.emit()
        else:
            self.finished.emit([])


class MyThread3_3(QThread):
    """
    This class get access to the database only once;
    Because of the multi-threading programming, the dictionary 'self.second_query_result' can be accessed directly;
    The store_id argument will be used in sql command since one sku_id might appear more than once in the same table;
    The logical part in the first sql query to restore the correct result changes a little bit;
    The first query gets the information about sku_id and group_id based on the cv_id;
    The second query is necessary since the group probably have some sku_id that the first query does not cover;
    """
    finished = pyqtSignal(object)
    error_connection = pyqtSignal()
    error_algorithm = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, store_id='2', db_user='root', db_pass='commaai2017',
                 db_database='hobin',
                 db_port='3306', db_host='127.0.0.1', **kwargs):
        """
        :param parent:
        :param store_id: The store_id will be used in sql command since one sku_id might appear more than once in the same table;
        :param logger_name:
        :param db_user:
        :param db_pass:
        :param db_database:
        :param db_port:
        :param db_host:
        :param kwargs:
        """
        super(MyThread3_3, self).__init__(parent)
        self.mysql_config = {
            'user': db_user,
            'password': db_pass,
            'port': int(db_port),
            'host': db_host,
            'database': db_database
        }
        self.conn = mysql.connector.connect(**self.mysql_config)

        # some variables
        self.mylogger3_3 = logging.getLogger(logger_name)
        self.parent = parent
        self.store_id = store_id
        self.first_sql_command_start = """
        select a.goods_name, a.goods_spec, a.sku_price, a.sku_id, a.goods_weight, b.group_id, a.cv_id from storegoods as a 
        left join cm_cvid_group_bind as b on a.sku_id= b.sku_id where a.store_id = %s and a.cv_id in 
        """ % self.store_id
        self.first_sql_tuple = ()
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        self.first_query_result = []
        self.group_info_refresh_needed = True
        self.second_sql_statement = """
        select a.goods_name, a.goods_spec, a.sku_price, a.sku_id, a.goods_weight, b.group_id, a.cv_id from storegoods as a 
        right join cm_cvid_group_bind as b on a.sku_id= b.sku_id 
        where a.store_id= %s order by group_id;
        """ % self.store_id
        self.second_query_result = {}
        self.mylogger3_3.info('Connection to database is successful')

    def query_cv_info(self):
        if len(self.detected_result) > 0:
            # 1, the configuration of the first sql command and sql tuple for cursor.execute()
            result_reduced = Counter(self.detected_result)
            first_sql_command_end = '('
            for _ in range(len(result_reduced)):
                first_sql_command_end = first_sql_command_end + '%s,'
            first_sql_command_end = first_sql_command_end[:-1] + ') order by cv_id'  # deleting the last element - comma.
            self.first_sql_tuple = tuple(
                result_reduced)  # changing the dictionary type to the tuple type as cursor.execute() requires.

            # 2, the execution of the sql querying
            cursor = self.conn.cursor()
            cursor.execute(self.first_sql_command_start + first_sql_command_end, self.first_sql_tuple)
            results_init = cursor.fetchall()  # a list of tuples

            # 3, restoring the correct result
            results_final = []
            if len(results_init) == len(self.detected_result):
                results_final = results_init
            else:
                if len(results_init) == len(result_reduced):
                    result_reduced_sorted = sorted(result_reduced.keys())
                    for index, key in enumerate(result_reduced_sorted):
                        for _ in range(result_reduced[key]):
                            results_final.append(results_init[index])
                else:
                    # the database might has no record for some cv_id;
                    reserved_key_list = []
                    for record_line in results_init:
                        # by default, the last element is the cv_id and the data type is int;
                        reserved_key_list.append(str(record_line[-1]))

                    # you must convert the str type back to the int type before sorting since the data type is int in database;
                    # Otherwise, the index of results_init[index] used in restoring the details, will cause the incorrect result;
                    result_double_reduced = {}
                    for reserved_key in reserved_key_list:
                        if result_reduced.get(reserved_key):
                            result_double_reduced[int(reserved_key)] = result_reduced.get(reserved_key)

                    # restoring the details
                    result_double_reduced_sorted = sorted(result_double_reduced.keys())
                    for index, key in enumerate(result_double_reduced_sorted):
                        for _ in range(result_double_reduced[key]):
                            results_final.append(results_init[index])

            # 4, the end of the first query;
            cursor.close()
            self.first_query_result = results_final
        else:
            self.first_query_result = []

    def query_group_info(self, group_id_index= -2):
        # The second query is necessary since the group probably have some sku_id that the first query does not cover;
        # adding where clause with store_id is to ensure that one sku_id has only one record;
        # In other words, one sku_id might have two or more records since different store arrange the sku_id from 0;
        cursor = self.conn.cursor()
        cursor.execute(self.second_sql_statement)
        group_info_result = cursor.fetchall()

        # assuming that all items of same group stays together, is implemented by using 'order by group_id' in sql_statement2;
        # grouping the list based on group_id for fast access;
        dict01 = {}
        current_group = 0
        start_index = 0
        end_index = 0
        last_index = len(group_info_result) - 1  # It is not used to do the slicing;
        for index, item in enumerate(group_info_result):
            if index == 0:
                current_group = item[group_id_index]
                start_index = index
                end_index = start_index + 1
            if current_group == item[group_id_index]:
                end_index = index + 1
                if index == last_index:
                    dict01[current_group] = group_info_result[start_index: end_index]
            else:
                # recording the information about last group since new group number appears;
                dict01[current_group] = group_info_result[start_index: end_index]
                current_group = item[group_id_index]
                start_index = index
                end_index = start_index + 1
                if index == last_index:
                    # This if statement may not be executed since one group has at least two records;
                    dict01[current_group] = group_info_result[start_index: end_index]

        # storing the final dictionary
        self.second_query_result = dict01
        self.mylogger3_3.info('SQL thread: the query about the group_id is given below.')
        for key in self.second_query_result.keys():
            self.mylogger3_3.info('key: %s' % key)
            self.mylogger3_3.info(self.second_query_result.get(key))
        self.mylogger3_3.info('--------------------------------------------------------------')
        # the end of second query
        cursor.close()

    def run(self):
        self.mylogger3_3.debug('SQL thread (begin): %s' % self.detected_result)
        try:
            if self.group_info_refresh_needed:
                self.mylogger3_3.debug('SQL thread begins to refresh the group information.')
                self.conn.close()
                self.conn = mysql.connector.connect(**self.mysql_config)
                self.query_group_info()
                self.group_info_refresh_needed = False
                self.mylogger3_3.debug('SQL thread ends to refresh the group information.')
            self.query_cv_info()
            self.mylogger3_3.debug('SQL thread (end): %s' % self.first_query_result)
            self.finished.emit(self.first_query_result)
        except mysql.connector.Error:
            self.mylogger3_3.error(
                '***------------------------Be careful! Error occurs in SQL thread!------------------------***',
                exc_info=True)
            self.conn.close()
            self.conn = mysql.connector.connect(**self.mysql_config)
            self.error_connection.emit()
        except BaseException:
            self.mylogger3_3.error(
                '***------------------------Be careful! Error occurs in SQL thread!------------------------***',
                exc_info=True)
            self.error_algorithm.emit()


class MyThread3_3_1(QThread):
    """
    Compared with the MyThread3_3 class, the group_info_refresh signal is emitted after the execution of query_group_info function;
    Compared with the MyThread3_3 class, the connection will be closed and reconnect to database due to the update;
    """
    finished = pyqtSignal(object)
    group_dict_refresh = pyqtSignal(object)
    error_connection = pyqtSignal()
    error_algorithm = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, store_id='2', db_user='root', db_pass='commaai2017',
                 db_database='hobin',
                 db_port='3306', db_host='127.0.0.1', **kwargs):
        """
        :param parent:
        :param store_id: The store_id will be used in sql command since one sku_id might appear more than once in the same table;
        :param logger_name:
        :param db_user:
        :param db_pass:
        :param db_database:
        :param db_port:
        :param db_host:
        :param kwargs:
        """
        super(MyThread3_3_1, self).__init__(parent)
        self.mysql_config = {
            'user': db_user,
            'password': db_pass,
            'port': int(db_port),
            'host': db_host,
            'database': db_database
        }
        self.conn = mysql.connector.connect(**self.mysql_config)

        # some variables
        self.mylogger3_3_1 = logging.getLogger(logger_name)
        self.parent = parent
        self.store_id = store_id
        self.first_sql_command_start = """
        select a.goods_name, a.goods_spec, a.sku_price, a.sku_id, a.goods_weight, b.group_id, a.cv_id from storegoods as a 
        left join cm_cvid_group_bind as b on a.sku_id= b.sku_id where a.store_id = %s and a.cv_id in 
        """ % self.store_id
        self.first_sql_tuple = ()
        self.detected_result = []  # the result of the detection of the ML Model and it is assigned in the QMainWindow class;
        self.first_query_result = []
        self.group_info_refresh_needed = True
        self.database_update_needed = False
        self.second_sql_statement = """
        select a.goods_name, a.goods_spec, a.sku_price, a.sku_id, a.goods_weight, b.group_id, a.cv_id from storegoods as a 
        right join cm_cvid_group_bind as b on a.sku_id= b.sku_id 
        where a.store_id= %s order by group_id;
        """ % self.store_id
        self.second_query_result = {}
        self.mylogger3_3_1.info('Connection to database is successful')

    def query_cv_info(self):
        if len(self.detected_result) > 0:
            # 1, the configuration of the first sql command and sql tuple for cursor.execute()
            result_reduced = Counter(self.detected_result)
            first_sql_command_end = '('
            for _ in range(len(result_reduced)):
                first_sql_command_end = first_sql_command_end + '%s,'
            first_sql_command_end = first_sql_command_end[:-1] + ') order by cv_id'  # deleting the last element - comma.
            self.first_sql_tuple = tuple(result_reduced)  # changing the dictionary type to the tuple type as cursor.execute() requires.

            # 2, the execution of the sql querying
            if self.database_update_needed:
                self.conn.close()
                self.conn = mysql.connector.connect(**self.mysql_config)
                self.database_update_needed = False
            cursor = self.conn.cursor()
            cursor.execute(self.first_sql_command_start + first_sql_command_end, self.first_sql_tuple)
            results_init = cursor.fetchall()  # a list of tuples

            # 3, restoring the correct result
            results_final = []
            if len(results_init) == len(self.detected_result):
                results_final = results_init
            else:
                if len(results_init) == len(result_reduced):
                    result_reduced_sorted = sorted(result_reduced.keys())
                    for index, key in enumerate(result_reduced_sorted):
                        for _ in range(result_reduced[key]):
                            results_final.append(results_init[index])
                else:
                    # the database might has no record for some cv_id;
                    reserved_key_list = []
                    for record_line in results_init:
                        # by default, the last element is the cv_id and the data type is int;
                        reserved_key_list.append(str(record_line[-1]))

                    # you must convert the str type back to the int type before sorting since the data type is int in database;
                    # Otherwise, the index of results_init[index] used in restoring the details, will cause the incorrect result;
                    result_double_reduced = {}
                    for reserved_key in reserved_key_list:
                        if result_reduced.get(reserved_key):
                            result_double_reduced[int(reserved_key)] = result_reduced.get(reserved_key)

                    # restoring the details
                    result_double_reduced_sorted = sorted(result_double_reduced.keys())
                    for index, key in enumerate(result_double_reduced_sorted):
                        for _ in range(result_double_reduced[key]):
                            results_final.append(results_init[index])

            # 4, the end of the first query;
            cursor.close()
            self.first_query_result = results_final
        else:
            self.first_query_result = []

    def query_group_info(self, group_id_index= -2):
        # The second query is necessary since the group probably have some sku_id that the first query does not cover;
        # adding where clause with store_id is to ensure that one sku_id has only one record;
        # In other words, one sku_id might have two or more records since different store arrange the sku_id from 0;
        cursor = self.conn.cursor()
        cursor.execute(self.second_sql_statement)
        group_info_result = cursor.fetchall()

        # assuming that all items of same group stays together, is implemented by using 'order by group_id' in sql_statement2;
        # grouping the list based on group_id for fast access;
        dict01 = {}
        current_group = 0
        start_index = 0
        end_index = 0
        last_index = len(group_info_result) - 1  # It is not used to do the slicing;
        for index, item in enumerate(group_info_result):
            if index == 0:
                current_group = item[group_id_index]
                start_index = index
                end_index = start_index + 1
            if current_group == item[group_id_index]:
                end_index = index + 1
                if index == last_index:
                    dict01[current_group] = group_info_result[start_index: end_index]
            else:
                # recording the information about last group since new group number appears;
                dict01[current_group] = group_info_result[start_index: end_index]
                current_group = item[group_id_index]
                start_index = index
                end_index = start_index + 1
                if index == last_index:
                    # This if statement may not be executed since one group has at least two records;
                    dict01[current_group] = group_info_result[start_index: end_index]

        # storing the final dictionary
        self.second_query_result = dict01
        self.mylogger3_3_1.info('SQL thread: the query about the group_id is given below.')
        for key in self.second_query_result.keys():
            self.mylogger3_3_1.info('key: %s' % key)
            self.mylogger3_3_1.info(self.second_query_result.get(key))
        self.mylogger3_3_1.info('--------------------------------------------------------------')

        # the end of second query
        cursor.close()

    def run(self):
        self.mylogger3_3_1.debug('SQL thread (begin): %s' % self.detected_result)
        try:
            if self.group_info_refresh_needed:
                self.mylogger3_3_1.debug('SQL thread begins to refresh the group information.')
                self.conn.close()
                self.conn = mysql.connector.connect(**self.mysql_config)
                self.query_group_info()
                self.group_dict_refresh.emit(self.second_query_result)
                # print(self.second_query_result)
                self.group_info_refresh_needed = False
                self.mylogger3_3_1.debug('SQL thread ends to refresh the group information.')
            self.query_cv_info()
            self.mylogger3_3_1.debug('SQL thread (end): %s' % self.first_query_result)
            # print(self.first_query_result)
            self.finished.emit(self.first_query_result)
        except mysql.connector.Error:
            self.mylogger3_3_1.error(
                '***------------------------Be careful! Error occurs in SQL thread!------------------------***',
                exc_info=True)
            self.conn.close()
            self.conn = mysql.connector.connect(**self.mysql_config)
            self.error_connection.emit()
        except BaseException:
            self.mylogger3_3_1.error(
                '***------------------------Be careful! Error occurs in SQL thread!------------------------***',
                exc_info=True)
            self.error_algorithm.emit()


if __name__ == '__main__':
    # test for memory leak
    # a = MyThread3_2()
    # a.start()
    # a.detected_result = ['589','460','460','589', '274','460']
    # counter = 0  # I have tested 500 times for MyThread3_2 class and there is no memory leak.
    # while counter > 0:
    #     while a.isRunning():
    #         pass
    #     counter = counter - 1
    #     a.start()
    # time.sleep(1)
    # print('The test finish successfully.')

    # test for functionality
    b = MyThread3_3_1()
    b.detected_result = ['460', '589', '3976', '285', '5762', '5762','192006']
    b.start()
    while b.isRunning():
        pass
