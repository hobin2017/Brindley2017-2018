"""
Payment System
author = hobin
version = 1.1.0
"""

import cv2
import qtmodern.styles
import qtmodern.windows
import sys
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout
# -----------------------------------------------------------------------------------------------
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
from CameraThread import MyThread2
from ML_Model import Detection1
from sqlThread import MyThread3


class PaymentSystem(QMainWindow):
    global app  # the QApplication

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Payment System')
        self.main_frame = QWidget()
        self.main_widget = MainLayout(self)
        self.stand_by_widget = StandbyLayout(self)
        self.main_frame.stacked_layout = QStackedLayout()
        self.main_frame.stacked_layout.addWidget(self.stand_by_widget)
        self.main_frame.stacked_layout.addWidget(self.main_widget)
        self.main_frame.setLayout(self.main_frame.stacked_layout)
        self.setCentralWidget(self.main_frame)
        self.showFullScreen() # no Min Button and no Max Button in the main layout
        self.main_widget.mainlayout.leftlayout.secondlayout.sendList.connect(self.main_widget.renewSum)


        # for switching the standby layout and main layout;
        self.capture1 = cv2.VideoCapture(1)
        self.capture1.set(3, 800)  # 3 indicates the width;
        self.capture1.set(4, 600)  # 4 indicates the height;
        self.thread2 = MyThread2(camera_object=self.capture1, parent=self)
        self.thread2.detected.connect(self.work1)
        self.thread2.start()

        # for work3
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.work3)

        # the start() of self.thread3 is used in work1();
        # thread3 is used to execute the run of thread0 (detection of products)
        self.thread3 = MyThread2(camera_object=self.capture1, rate_detect=0.02, parent=self)
        self.thread3.detected.connect(self.work4)

        # thread4 is about the SQL statement
        self.thread4 = MyThread3(parent=self)
        self.thread4.finished.connect(self.work5)


        # for ML Model
        #  it's start() is used in work1();
        self.thread0 = Detection1(camera_object=self.capture1, parent=self)
        self.thread0.detected.connect(self.work2)


    def work1(self):
        """
        Aim: switching the layout from standby to main;
        Requirement:
        stopping the CameraThread and starting the timer
        Optimization:
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        But you don't know which one is working.
        """
        self.thread2.quit()  # I guess, it does not release the camera. Yes!
        self.main_frame.stacked_layout.setCurrentWidget(self.main_widget)
        self.timer1.start(120000)  # unit: second;
        self.thread3.start()



    def work2(self, result_detected):
        """
        After the result of detection is done, we run the thread4 to use the result and query the database;
        After the querying, thread4 initiate the work5() to refresh the GUI;
        :param result_detected: a list;
        :return: a list of detected product;
        """
        self.thread4.detected_result = result_detected
        self.thread4.start()



    def work3(self):
        """
        when there is no action, returns to the standby layout;
        """
        self.timer1.stop()
        self.main_frame.stacked_layout.setCurrentWidget(self.stand_by_widget)
        time.sleep(0.3)
        self.thread2.start()  # Ideally, this is not the first time to starting this thread! It is a re-start!


    def work4(self):
        """
        This function is initialized by the 'detected' signal of self.thread3;
        """
        self.thread3.quit()
        self.thread0.start()
        while self.thread0.isRunning():
            app.processEvents()
        self.thread3.start()


    def work5(self, result_sql):
        """
        To refresh my ShoppingList widget
        :param result_sql: a list of tuples;
        :return:
        """
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct(result_sql)


    def closeEvent(self, event):
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.quit() # The first way to stop the thread.
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread
        self.thread2.quit()
        self.main_widget.mainlayout.rightlayout.secondlayout.capture0.release()
        self.capture1.release()
        self.thread4.conn.close()


if __name__ == '__main__':
    global app
    global mainwindow
    try:
        app = QApplication(sys.argv)
        mainwindow = PaymentSystem()
        # ----------using qtmordern ------------------------------
        qtmodern.styles.dark(app)
        mywindow = qtmodern.windows.ModernWindow(mainwindow)
        mywindow.show()
        # ----------------------------------------------------------------------
        # mainwindow.show()
        sys.exit(app.exec_())
    except BaseException:
        # mainwindow.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread
        mainwindow.main_widget.mainlayout.rightlayout.secondlayout.capture0.release()
        mainwindow.capture1.release()
        mainwindow.main_widget.mainlayout.rightlayout.secondlayout.thread1.quit()
        mainwindow.thread2.quit()
        mainwindow.thread4.conn.close()
        mainwindow.thread0.sess.close()

