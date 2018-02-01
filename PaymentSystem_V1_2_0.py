"""
Payment System
author = hobin
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
from AccountThread import MyThread4_1
from QRcodeThread import MyThread5
from UserTrackingThread import MyThread6_1

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

        # thread5 is about the account detection
        self.thread5 = MyThread4_1(parent=self)
        self.thread5.success.connect(self.work6)
        self.thread5.failed_detection_web.connect(self.work7)
        self.thread5.failed_detection_local.connect(self.work7)
        self.thread5.timeout_http.connect(self.work10)

        # thread6 is about the QR code thread
        self.thread6 = MyThread5(parent=self)
        self.thread6.finished.connect(self.work8)

        # thread7 is about the user-checking thread to help account thread
        self.thread7 = MyThread6_1(parent=self)
        self.thread7.tracking_failed.connect(self.work9)

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
        # self.thread2.quit()  # I guess, it does not release the camera. Yes!
        self.thread2.status = False
        while self.thread2.isRunning():
            # for verifying whether the main process will wait for the end of self.thread2 and answer: Yes;
            # print('waiting for thread2 stops')
            pass
        print('thread2 has stopped.')
        self.main_frame.stacked_layout.setCurrentWidget(self.main_widget)
        self.timer1.start(120000)  # unit: second;
        self.thread3.start()
        self.thread5.start()


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
        It is executed by a QTimer;
        """
        self.timer1.stop()
        self.thread3.status = False
        self.main_frame.stacked_layout.setCurrentWidget(self.stand_by_widget)
        time.sleep(0.3)
        self.thread2.start()  # Ideally, this is not the first time to starting this thread! It is a re-start!


    def work4(self):
        """
        This function is initialized by the 'detected' signal of self.thread3;
        """
        # self.thread3.quit()  # it doesn't stop the thread3 since thread3 is a infinite loop;
        print('------------------------------start a new ML calculation---------------------------------------------')
        print('work4 begins')
        self.thread3.status = False  # this can stop the thread3
        while self.thread3.isRunning():
            # for verifying whether the main process will wait for the end of self.thread2 and answer: Yes;
            # print('waiting for thread3 stops')
            pass
        print('thread3 has stopped.')
        self.thread0.start()
        print('work4 ends')


    def work5(self, result_sql):
        """
        To refresh my ShoppingList widget
        :param result_sql: a list of tuples;
        :return:
        """
        print('work5 begins')
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct(result_sql)
        self.thread6.dict01['buy_skuids'] = ','.join([str(product[3]) for product in result_sql])
        self.thread6.start()
        self.thread3.start()
        print('work5 ends')


    def work6(self, user_name, user_img):
        """
        to refresh the information about the account only if detection successes;
        :return:
        """
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText(user_name)
        self.main_widget.mainlayout.rightlayout.firstlayout.imgUser.loadFromData(user_img)
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(self.main_widget.mainlayout.rightlayout.firstlayout.imgUser.scaled(80, 80))
        self.thread7.start()
        
        
    def work7(self):
        """
        to refresh the information about the account when there is no well-matched user;
        :return: 
        """
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)


    def work8(self, img_qrcode):
        # print('work8 begins')
        if img_qrcode == None:
            self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        else:
            self.main_widget.mainlayout.rightlayout.img_qrcode.convertFromImage(img_qrcode)
            self.main_widget.mainlayout.rightlayout.thirdlayout.setPixmap(self.main_widget.mainlayout.rightlayout.img_qrcode.scaled(300, 300))
        # print('work8 ends')


    def work9(self):
        """
        The primary user is gone therefore the account thread should work again;
        """
        # print('work9 begins')
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)
        self.thread5.start()
        # print('work9 ends')


    def work10(self):
        """
        The account thread should restart since the network problem(timeout problem);
        """
        self.thread5.start()


    def closeEvent(self, event):
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.quit() # The first way to stop the thread.
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread
        self.thread2.status = False
        self.main_widget.mainlayout.rightlayout.secondlayout.capture0.release()
        self.capture1.release()
        self.thread4.conn.close()


if __name__ == '__main__':
    global app
    global mainwindow  # used in the exception part
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
        mainwindow.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False
        mainwindow.thread2.status = False
        mainwindow.thread3.status = False
        mainwindow.thread6.status = False
        mainwindow.thread7.status = False
        mainwindow.thread5.quit()
        mainwindow.thread6.quit()
        mainwindow.thread7.quit()
        mainwindow.thread4.conn.close()
        mainwindow.thread4.quit()
        mainwindow.thread0.sess.close()
        mainwindow.thread0.quit()


