"""
Thread for SQL statements
author = hobin
"""
import mysql.connector
import logging
from PyQt5.QtCore import QThread, pyqtSignal


class MyThread3(QThread):
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        """
        :param detected_result: the result of the detection of the ML Model; currently it is a list;
        :param parent:
        """
        super(MyThread3, self).__init__(parent)
        self.parent = parent
        self.detected_result = []  # It is assigned in the QMainWindow class;
        self.conn = mysql.connector.connect(user='root', password='qwerQWER', database='hobin')
        print('Connection to database is successful')


    def run(self):
        print('SQL Thread (begin): %s'% self.detected_result)
        results = []
        if len(self.detected_result)>=0:
            cursor = self.conn.cursor()
            for i in self.detected_result:
                cursor.execute('select goods_name, goods_spec, sku_price, sku_id from storegoods where cv_id = %s', (i,))
                results = results + cursor.fetchall()
            print('SQL result (end): %s'% results)
            cursor.close()
            self.finished.emit(results)


class MyThread3_1(QThread):
    """
    Compared with the MyThread3 class, the logging module is introduced to this module at first time.
    detected_result: the result of the detection of the ML Model; currently it is a list;
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
        self.detected_result = []  # It is assigned in the QMainWindow class;
        # print('Connection to database is successful')
        self.mylogger3_1.info('Connection to database is successful')


    def run(self):
        # print('SQL Thread (begin): %s'% self.detected_result)
        self.mylogger3_1.debug('SQL Thread (begin): %s'% self.detected_result)
        results = []
        if len(self.detected_result)>=0:
            cursor = self.conn.cursor()
            for i in self.detected_result:
                cursor.execute('select goods_name, goods_spec, sku_price, sku_id from storegoods where cv_id = %s', (i,))
                results = results + cursor.fetchall()
            # print('SQL result (end): %s'% results)
            self.mylogger3_1.debug('SQL result (end): %s'% results)
            cursor.close()
            self.finished.emit(results)


if __name__ == '__main__':
    a = MyThread3()
    a.start()
    while a.isRunning():
        pass
    print('done')

