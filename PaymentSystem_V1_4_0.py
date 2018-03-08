# -*- coding: utf-8 -*-
"""
Payment System
author: hobin
"""


import cv2
import qtmodern.styles
import qtmodern.windows
import sys
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout
# -----------------------------------------------------------------------------------------------
from qtMediaPlayer import MyMediaPlayer
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
from EndLayout import EndLayout
from CameraThread import MyThread2
from ML_Model import Detection1_1, Detection2_1
from sqlThread import MyThread3
from AccountThread import MyThread4_3
from QRcodeThread import MyThread5
from UserTrackingThread import MyThread6_3
from GesturePayThread import MyThread7
from WebSocketClientThread import MyThread8


class PaymentSystem(QMainWindow):
    global app  # the QApplication

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Payment System')
        self.main_frame = QWidget()
        self.main_widget = MainLayout(self)
        self.stand_by_widget = StandbyLayout(self)
        self.end_widget_success = EndLayout(parent=self, img_path='.//Images//pay_success.png')
        self.end_widget_error = EndLayout(parent=self, img_path='.//Images//pay_error.png')
        self.main_frame.stacked_layout = QStackedLayout()
        self.main_frame.stacked_layout.addWidget(self.stand_by_widget)
        self.main_frame.stacked_layout.addWidget(self.main_widget)
        self.main_frame.stacked_layout.addWidget(self.end_widget_success)
        self.main_frame.stacked_layout.addWidget(self.end_widget_error)
        self.main_frame.setLayout(self.main_frame.stacked_layout)
        self.setCentralWidget(self.main_frame)
        self.showFullScreen()  # no Min Button and no Max Button in the main layout
        self.main_widget.mainlayout.leftlayout.secondlayout.sendList.connect(self.main_widget.renewSum)

        # media player
        self.media_player = MyMediaPlayer(self)

        # for switching the standby layout and main layout;
        self.capture1 = cv2.VideoCapture(1)
        self.capture1.set(3, 800)  # 3 indicates the width;
        self.capture1.set(4, 600)  # 4 indicates the height;
        self.thread2 = MyThread2(camera_object=self.capture1, parent=self)
        self.thread2.detected.connect(self.work1)

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
        self.thread5 = MyThread4_3(parent=self)
        self.thread5.success.connect(self.work6)
        self.thread5.failed_detection_web.connect(self.work7)
        self.thread5.failed_detection_local.connect(self.work7)
        self.thread5.timeout_http.connect(self.error01)
        self.thread5.wechatpay_entrust.connect(self.work14)

        # thread6 is about the QR code thread
        self.thread6 = MyThread5(parent=self)
        self.thread6.finished.connect(self.work8)

        # thread7 is about the user-checking thread to help account thread
        self.thread7 = MyThread6_3(parent=self)
        self.thread7.tracking_failed.connect(self.work9)

        # thread8 is about the gesture-pay thread
        self.thread8 = MyThread7()
        self.thread8.finished_error.connect(self.work12)
        self.thread8.timeout_http.connect(self.error02)

        # thread9 is about the websocket thread
        self.thread9 = MyThread8()
        self.thread9.payclear_success.connect(self.work11)
        self.thread9.payclear_failure.connect(self.work12)
        self.thread9.opendoor.connect(self.work13)
        self.thread9.start()
        self.timer9 = QTimer()
        self.timer9.timeout.connect(self.thread9.ping_timer)
        self.timer9.start(60000)

        # for ML Model
        #  it's start() is used in work1();
        self.thread0 = Detection1_1(camera_object=self.capture1, parent=self)
        self.thread0.detected.connect(self.work2)

        # ML Model for hand detection
        self.new_user_flag = True
        self.new_order_flag = True
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.thread00 = Detection2_1(parent=self)
        self.thread00.detected.connect(self.work10)

        #
        self.thread2.start()

    def work1(self):
        """
        Aim: switching the layout from standby to main;
        Requirement:
        stopping the CameraThread and starting the timer
        Optimization:
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        But you don't know which one is working.
        """
        self.main_frame.stacked_layout.setCurrentWidget(self.main_widget)
        self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
            self.main_widget.mainlayout.rightlayout.secondlayout)
        self.timer1.start(120000)  # unit: second;
        self.thread3.start()
        self.thread5.start()
        self.thread00.start()

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
        self.thread5.status = False
        self.thread7.status = False
        self.thread00.status = False
        self.main_frame.stacked_layout.setCurrentWidget(self.stand_by_widget)
        time.sleep(2)
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.thread3.status = False
        self.thread5.status = False
        self.thread7.status = False
        self.thread00.status = False
        self.main_widget.mainlayout.leftlayout.firstlayout.label2.setText('0.0')
        self.main_widget.mainlayout.leftlayout.secondlayout.clear()
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)
        self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        print('--------------------------------Clear, Ready for next transaction---------------------------------')
        self.thread2.start()  # Ideally, this is not the first time to starting this thread! It is a re-start!

    def work4(self):
        """
        This function is initialized by the 'detected' signal of self.thread3;
        """
        # self.thread3.quit()  # it doesn't stop the thread3 since thread3 is a infinite loop;
        self.order_number = 'invalid'
        self.new_order_flag = True
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
        print('work5 ends')

    def work6(self, user_name, user_img):
        """
        to refresh the information about the account only if detection successes;
        :return:
        """
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText(user_name)
        self.main_widget.mainlayout.rightlayout.firstlayout.imgUser.loadFromData(user_img)
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgUser.scaled(80, 80))
        self.user_id = self.thread5.dict02['data']['user_id']
        self.new_user_flag = False
        self.main_widget.mainlayout.rightlayout.secondlayout.icon01.setVisible(True)
        self.thread7.start()

    def work7(self):
        """
        to refresh the information about the account when there is no well-matched user;
        :return:
        """
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)

    def work8(self, img_qrcode):
        # print('work8 begins')
        if img_qrcode == None:
            self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
            self.order_number = 'invalid'
            self.new_order_flag = True
        else:
            self.main_widget.mainlayout.rightlayout.img_qrcode.convertFromImage(img_qrcode)
            self.main_widget.mainlayout.rightlayout.thirdlayout.setPixmap(
                self.main_widget.mainlayout.rightlayout.img_qrcode.scaled(300, 300))
            self.order_number = self.thread6.dict02['data']['order_no']
            self.new_order_flag = False
        self.thread3.start()
        # print('work8 ends')

    def work9(self):
        """
        The primary user is gone therefore the account thread should work again;
        """
        # print('work9 begins')
        self.user_id = 'invalid'
        self.new_user_flag = True
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)
        self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
            self.main_widget.mainlayout.rightlayout.secondlayout)
        self.thread5.start()
        self.main_widget.mainlayout.rightlayout.secondlayout.icon01.setVisible(False)
        # print('work9 ends')

    def work10(self):
        """
        Keyword Error might happens if work10 starts and the user id or the order number are none;
        the information about the user id and the order number might be out of date;
        """
        # print('work10 begins')
        if self.user_id == 'invalid' or self.order_number == 'invalid':
            print('work10 (end): the user id or the order number is invalid.')
            self.thread00.start()
        else:
            # self.main_widget.mainlayout.rightlayout.secondlayout.movie.stop()
            self.main_widget.mainlayout.rightlayout.secondlayout.icon01.setVisible(False)
            self.thread8.dict01['user_id'] = self.user_id
            self.thread8.dict01['order_no'] = self.order_number
            self.thread8.start()
        # print('work10 ends')

    def work11(self):
        """My server says that the gesture-pay is successful which indicates the end of such transaction"""
        # print('work11 begins')
        self.main_frame.stacked_layout.setCurrentWidget(self.end_widget_success)
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file05)
        self.media_player.player.play()
        # print('work11 ends')

    def work12(self):
        """My server says that the gesture-pay is failed since one user only can pay 5 times everyday"""
        print('work12 begins')
        self.main_frame.stacked_layout.setCurrentWidget(self.end_widget_error)
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        print('work12 ends')

    def work13(self, door_id):
        """My server says opening the specific door."""
        pass

    def work14(self, wechatpay_entrust):
        """
        :param wechatpay_entrust: indicating whether the user can show the thumbs-up to finish the payment;;
        :return:
        """
        # print('work14 begins')
        if wechatpay_entrust == 0:
            self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
                self.main_widget.mainlayout.rightlayout.secondlayout_2ndWidget)
        elif wechatpay_entrust == 1:
            self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
                self.main_widget.mainlayout.rightlayout.secondlayout)
        # print('work14 ends')

    def error01(self):
        """
        The account thread should restart since the network problem(timeout problem);
        """
        self.thread5.start()

    def error02(self):
        """
        Timeout error happens in the gesture-order thread, the gesture order thread should run again;
        """
        self.thread8.dict01['user_id'] = self.user_id
        self.thread8.dict01['order_no'] = self.order_number
        self.thread8.start()

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
    except BaseException as e:
        # mainwindow.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread
        mainwindow.main_widget.mainlayout.rightlayout.secondlayout.capture0.release()
        mainwindow.capture1.release()
        mainwindow.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False
        mainwindow.thread2.status = False
        mainwindow.thread3.status = False
        mainwindow.thread6.status = False
        mainwindow.thread7.status = False
        mainwindow.thread8.status = False
        mainwindow.thread5.quit()
        mainwindow.thread6.quit()
        mainwindow.thread7.quit()
        mainwindow.thread8.quit()
        mainwindow.thread9.quit()
        mainwindow.thread4.conn.close()
        mainwindow.thread4.quit()
        mainwindow.thread0.quit()
        mainwindow.thread00.sess.close()
        mainwindow.thread00.quit()
        print(e)
        print('---------------------------Error happens, restart the app----------------------------------')
        sys.exit()




