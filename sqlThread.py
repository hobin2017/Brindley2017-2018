"""
Thread for SQL statements
author = hobin
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
        else:
            self.finished.emit([])




if __name__ == '__main__':
    a = MyThread3_2()
    a.start()
    a.detected_result = ['589','460','460','589', '274','460']
    counter = 0  # I have tested 500 times for MyThread3_2 class and there is no memory leak.
    while counter > 0:
        while a.isRunning():
            pass
        counter = counter - 1
        a.start()
    time.sleep(1)
    print('The test finish successfully.')

