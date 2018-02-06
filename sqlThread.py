"""
Thread for SQL statements
author = hobin
"""
import mysql.connector
from PyQt5.QtCore import QThread, pyqtSignal


class MyThread3(QThread):
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        """
        :param detected_object: the result of the detection of the ML Model; currently it is a list;
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


if __name__ == '__main__':
    a = MyThread3()
    a.start()
    while a.isRunning():
        pass
    print('done')

