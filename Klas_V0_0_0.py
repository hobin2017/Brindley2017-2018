# -*- coding: utf-8 -*-
"""
Payment System
author: hobin;
email = '627227669@qq.com';
"""
import copy
import cv2
import sys
import time

import os

import gc
from PyQt5.QtCore import QTimer, QThread, QIODevice
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout
# -----------------------------------------------------------------------------------------------
from qtMediaPlayer import MyMediaPlayer
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
from EndLayout import EndLayout
from CameraLayout import CameraDialog
from CameraThread import MyThread2_1
from ML_Model import Detection1_2_1, Detection2_4_1
from sqlThread import MyThread3_2_1
from AccountThread import MyThread4_4_1
from QRcodeThread import MyThread5_2
from UserTrackingThread import MyThread6_3_1
from GesturePayThread import MyThread7_1
from WebSocketClientThread import MyThread8_1
from ImageUploadThread import MyThread9_1
from Weigher import Weigher1_1, Weigher2
from ConfiguringModule import MyConfig1
from LoggingModule import MyLogging1
from StatisticsMethod import verifyWeight2
from Selfcheck import necessaryCheck_linux
from ReminderLayout import ReminderWeight02
from UserGuide import UserGuide03linux01

class PaymentSystem(QMainWindow):

    def __init__(self, **kwargs):
        super(PaymentSystem, self).__init__()
        # configuration
        self.myconfig = MyConfig1()

        # user guide
        if self.myconfig.data['operating_mode']['need_guide'] == '1':
            a = UserGuide03linux01()
            reply = a.exec()
            if reply != 0:
                sys.exit('Error happens in user guide, please start again')

        # logging
        self.mylogging = MyLogging1(logger_name='hobin')
        self.mylogging.logger.info('------------------Klas starts------------------------------------')


        # necessary check before Klas works
        if self.myconfig.data['necessary_check']['check_required'] == '1':
            necessaryCheck_linux(**self.myconfig.data)

        # all file path configuration
        self.project_path = os.path.dirname(__file__)
        # the expected outcome is like './Images';
        self.image_path = os.path.join(self.project_path, 'Images')
        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path)
        self.image_pay_success = os.path.join(self.image_path, 'pay_success.png')
        self.image_pay_error = os.path.join(self.image_path, 'pay_error.png')
        # the expected outcome is like './working_images';
        self.working_images_path = os.path.join(self.project_path, 'working_images')
        if not os.path.exists(self.working_images_path):
            os.makedirs(self.working_images_path)

        # layout management
        self.setWindowTitle('Payment System')
        self.main_frame = QWidget()
        self.main_widget = MainLayout(self, **self.myconfig.data['cam_user'])
        self.stand_by_widget = StandbyLayout(self)
        self.end_widget_success = EndLayout(parent=self, img_path=self.image_pay_success)
        self.end_widget_error = EndLayout(parent=self, img_path=self.image_pay_error)
        self.main_frame.stacked_layout = QStackedLayout()
        self.main_frame.stacked_layout.addWidget(self.stand_by_widget)
        self.main_frame.stacked_layout.addWidget(self.main_widget)
        self.main_frame.stacked_layout.addWidget(self.end_widget_success)
        self.main_frame.stacked_layout.addWidget(self.end_widget_error)
        self.main_frame.setLayout(self.main_frame.stacked_layout)
        self.setCentralWidget(self.main_frame)
        self.showMaximized()
        # self.showFullScreen()  # no Min Button and no Max Button in the main layout
        self.main_widget.mainlayout.leftlayout.secondlayout.sendList.connect(self.main_widget.renewSum)

        # other UI component
        # This reminder is currently used in sql_work5 function.
        self.reminder_weight_wrong_status = False  # True indicates the reminder is visible.
        self.reminder_weight_wrong = ReminderWeight02()

        # media player
        self.media_player = MyMediaPlayer(self)

        # item camera
        self.capture1 = cv2.VideoCapture(int(self.myconfig.data['cam_item']['cam_num']))
        self.capture1.set(3, int(self.myconfig.data['cam_item']['width']))  # 3 indicates the width;
        self.capture1.set(4, int(self.myconfig.data['cam_item']['height']))  # 4 indicates the height;

        # for switching the standby layout and main layout;
        # self.thread2 = MyThread2_1(camera_object=self.capture1, parent=self, logger_name='hobin')
        # self.thread2.detected.connect(self.weigher1_work1)
        self.weigher1 = Weigher1_1(**self.myconfig.data['weigher'])
        self.weigher1.detect_plus.connect(self.weigher1_work1)

        # showing the camera frame for items
        if self.myconfig.data['operating_mode']['isdebug'] == '1':
            self.camera_dialog = CameraDialog(camera_object=self.capture1)
            self.camera_dialog.show()

        # for shopping_timer_work3
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.shopping_timer_work3)

        # the start() of self.thread3 is used in weigher1_work1();
        # thread3 is used to execute the run of thread0_0 (detection of products)
        # self.thread3 = MyThread2_1(camera_object=self.capture1, rate_detect=0.02, parent=self, logger_name='hobin')
        # self.thread3.detected.connect(self.camera_diff_work4)
        self.record_weight = 0.0
        self.weigher2 = Weigher2(**self.myconfig.data['weigher'])
        self.weigher2.empty.connect(self.weigher2_work4b)
        self.weigher2.detect_changed.connect(self.weigher2_work4c)

        # thread4 is about the SQL statement
        self.thread4 = MyThread3_2_1(parent=self, **self.myconfig.data['db'])
        self.thread4.finished.connect(self.sql_work5)
        self.thread4.error_connection.connect(self.sql_error05)

        # thread5 is about the account detection
        self.thread5 = MyThread4_4_1(parent=self, **self.myconfig.data['account'])
        # self.thread5.setPriority(QThread.HighestPriority)
        self.thread5.success.connect(self.account_work6)
        self.thread5.upload_img.connect(self.account_work15c)
        self.thread5.failed_detection_web.connect(self.account_work7)
        self.thread5.failed_detection_local.connect(self.account_work7)
        self.thread5.timeout_http.connect(self.account_error01)
        self.thread5.wechatpay_entrust.connect(self.account_work14)

        # thread6 is about the QR code thread
        self.thread6 = MyThread5_2(parent=self, **self.myconfig.data['order'])
        self.thread6.finished.connect(self.order_work8)
        self.thread6.timeout_network.connect(self.order_error04)

        # thread7 is about the user-checking thread to help account thread
        self.thread7 = MyThread6_3_1(parent=self, **self.myconfig.data['user_tracking'])
        self.thread7.tracking_failed.connect(self.user_tracking_work9)

        # thread8 is about the gesture-pay thread
        self.thread8 = MyThread7_1(**self.myconfig.data['gesture_pay'])
        self.thread8.finished_error.connect(self.gesture_pay_work12)
        self.thread8.timeout_http.connect(self.gesture_pay_error02)

        # thread9 is about the websocket thread
        self.thread9 = MyThread8_1(**self.myconfig.data['websocket'])
        self.thread9.payclear_success.connect(self.websocket_work11)
        self.thread9.payclear_failure.connect(self.websocket_work12)
        self.thread9.opendoor.connect(self.websocket_work13)
        self.thread9.start()
        self.timer9 = QTimer()
        self.timer9.timeout.connect(self.thread9.ping_timer)
        self.timer9.start(60000)

        # thread10 is about the image-uploading thread
        self.gesture_img = None
        self.gesture_time = None
        self.items_img = None
        self.items_time = None
        self.user_img = None
        self.user_time = None
        self.thread10 = MyThread9_1(**self.myconfig.data['image_upload'])
        self.thread10.error.connect(self.image_upload_error03)

        # ML Model for item detection
        #  it's start() is used in camera_diff_work4;
        self.thread0_1 = Detection1_2_1(camera_object=self.capture1, parent=self, **self.myconfig.data['ml_item'])
        self.thread0_1.detected.connect(self.ml_item_work2)
        self.thread0_1.upload_img.connect(self.ml_item_work15b)
        # self.thread0_1.detect_same.connect(self.ml_item_work2b)
        # self.thread0_1.detect_empty_same.connect(self.ml_item_work2c)
        # self.thread0_1.detect_empty_diff.connect(self.ml_item_work2d)

        # ML Model for hand detection
        self.new_user_flag = True
        self.new_order_flag = True
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.thread0_0 = Detection2_4_1(parent=self, **self.myconfig.data['ml_hand'])
        # self.thread0_0.setPriority(QThread.HighPriority)
        self.thread0_0.detected.connect(self.ml_gesture_work10)
        self.thread0_0.upload_image.connect(self.ml_gesture_work15a)

        #
        del self.image_pay_success
        del self.image_pay_error
        self.mylogging.logger.info('------------------Klas is ready to work------------------------------------')
        # self.thread2.start()
        if self.weigher1.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('the first connection of the weigher1 is successful.')
        else:
            self.mylogging.logger.info('the first connection of the weigher1 is failed.')

    def weigher1_work1(self):
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
        self.mylogging.logger.info(
            '--------------------------------Next transaction begins!---------------------------------********')
        self.timer1.start(24*60*1000)  # unit: millisecond;
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('reconenction of the weigher2 is successful at weigher1_work1.')
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at weigher1_work1.')
        self.thread5.start()
        self.thread0_0.start()

    def ml_item_work2(self, result_detected):
        """
        The ML_item model says that the current result is not empty and it is different from the last result (Detection1_2_2 class).
        After the result of detection is done, we run the thread4 to use the result and query the database;
        After the querying, thread4 initiate the sql_work5() to refresh the GUI;
        :param result_detected: a list;
        :return: a list of detected product;
        """
        self.thread4.detected_result = result_detected
        self.thread4.start()

    def ml_item_work2b(self):
        """
        The ML_item model says that the current result is not empty but they are the same (Detection1_2_2 class).
        The ML_item model says that the current result is the same as the last result (Detection1_2_3 class).
        """
        self.new_order_flag = False
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            # self.mylogging.logger.info('reconenction of the weigher2 is successful at ml_item_work2b.')
            pass
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at ml_item_work2b.')

    def ml_item_work2c(self):
        """
        The ML_item model says that current result is empty and the last result also is empty.
        """
        self.order_number = 'invalid'  # self.new_order_flag = True at this time;
        self.thread0_1.last_result = []
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            # self.mylogging.logger.info('reconenction of the weigher2 is successful at ml_item_work2c.')
            pass
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at ml_item_work2c.')

    def ml_item_work2d(self):
        """
        The ML_item model says that the current result is empty but the last result is not empty.
        Therefore, I need to refresh the order information.
        """
        self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([])
        self.order_number = 'invalid'  # self.new_order_flag = True at this time;
        self.thread0_1.last_result = []
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            # self.mylogging.logger.info('reconenction of the weigher2 is successful at ml_item_work2d.')
            pass
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at ml_item_work2d.')

    def shopping_timer_work3(self):
        """
        when there is no action, returns to the standby layout;
        It is executed by a QTimer;
        """
        self.timer1.stop()
        # self.thread3.status = False
        self.weigher2.serial.close()
        self.weigher1.record_value = self.weigher2.record_value
        self.weigher2.record_value = 0.0
        self.thread5.status = False
        self.thread7.status = False
        self.thread0_0.status = False
        self.main_frame.stacked_layout.setCurrentWidget(self.stand_by_widget)
        if self.reminder_weight_wrong_status:
            self.reminder_weight_wrong.setHidden(True)
            self.reminder_weight_wrong_status = False
        time.sleep(2)
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.thread0_1.last_result = []  # If you do not refresh it, the last detected result comes from the last transaction.
        # self.thread3.status = False
        # self.weigher2.serial.close()
        self.thread5.status = False
        self.thread7.status = False
        self.thread0_0.status = False
        self.main_widget.mainlayout.leftlayout.firstlayout.label2.setText('0.0')
        self.main_widget.mainlayout.leftlayout.secondlayout.clear()
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)
        self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        gc.collect()
        self.mylogging.logger.info('--------------------------------Clear, Ready for next transaction---------------------------------********')
        # print('--------------------------------Clear, Ready for next transaction---------------------------------')
        # self.thread2.start()  # Ideally, this is not the first time to starting this thread! It is a re-start!
        if self.weigher1.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('connection of the weigher1 is successful at shopping_timer_work3.')
        else:
            self.mylogging.logger.info('connection of the weigher1 is failed at shopping_timer_work3.')

    def camera_diff_work4(self):
        """
        This function is initialized by the 'detected' signal of self.thread3;
        """
        self.new_order_flag = True
        self.mylogging.logger.info('------------------------------start a new ML calculation---------------------------------------------')
        # print('------------------------------start a new ML calculation---------------------------------------------')
        # print('camera_diff_work4 begins')
        self.thread0_1.start()
        # print('camera_diff_work4 ends')

    def weigher2_work4b(self):
        """
        This function is initialized by the empty signal of self.weigher2;
        This function is to clear the information about the order since the current weight is zero.
        The self.weigher2 still works when this function is executed.
        """
        self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([])
        self.order_number = 'invalid'
        self.new_order_flag = True
        self.thread0_1.last_result = []  # the communication between weigher and the ML Model for the ShoppingList Layout.
        self.reminder_weight_wrong.label1.setText('The current weight is 0.')
        if not self.reminder_weight_wrong_status:
            self.reminder_weight_wrong.setVisible(True)
            self.reminder_weight_wrong_status = True

    def weigher2_work4c(self, record_weight):
        """
        This function is initialized by the 'detect_changed' signal of self.weigher2;
        """
        self.new_order_flag = True
        self.mylogging.logger.info(
            '------------------------------start a new ML calculation---------------------------------------------')
        self.record_weight = record_weight
        # print('weigher2_work4c begins')
        self.thread0_1.start()
        # print('weigher2_work4c ends')

    def sql_work5(self, result_sql):
        """
        To refresh my ShoppingList widget
        :param result_sql: a list of tuples;
        :return:
        """
        # self.mylogging.logger.info('sql_work5 begins')
        # print('sql_work5 begins')

        # without verification
        # self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct(result_sql)
        # self.thread6.dict01['buy_skuids'] = ','.join([str(product[3]) for product in result_sql])
        # self.thread6.start()

        # with verification
        weight_range = verifyWeight2(result_sql)
        if weight_range[0] <= self.record_weight <= weight_range[1]:
            if self.reminder_weight_wrong_status:
                self.reminder_weight_wrong.setHidden(True)
                self.reminder_weight_wrong_status = False
            # Be careful the result_sql might be empty.
            self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct(result_sql)
            self.thread6.dict01['buy_skuids'] = ','.join([str(product[3]) for product in result_sql])
            self.thread6.start()
        else:
            # if the order number exists, set them to the default situation.
            self.thread0_1.last_result = []
            if self.order_number != 'invalid':
                self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
                self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([])
                self.order_number = 'invalid'
            # reminding the customer to place those item again
            self.reminder_weight_wrong.label1.setText('The record value is %s and it is not in range (%.2f,%.2f)'
                                                      % (self.record_weight, weight_range[0],weight_range[1]))
            if not self.reminder_weight_wrong_status:
                self.reminder_weight_wrong.setVisible(True)
                self.reminder_weight_wrong_status = True
            # self.thread3.start()
            if self.weigher2.serial.open(QIODevice.ReadOnly):
                # self.mylogging.logger.info('reconenction of the weigher2 is successful at sql_work5.')
                pass
            else:
                self.mylogging.logger.info('reconenction of the weigher2 is failed at sql_work5.')

        # self.mylogging.logger.info('sql_work5 ends')
        # print('sql_work5 ends')

    def account_work6(self, user_name, user_img):
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
        while self.thread5.isRunning():
            self.mylogging.logger.info('waits for account thread to stops and then starts the user-tracking thread.')
            # print('waiting for account thread to stops and then starts the user-tracking thread.')
            time.sleep(0.5)  # the account thread can be in running status (not finished status) at this point.
        self.thread7.start()

    def account_work7(self):
        """
        to refresh the information about the account when there is no well-matched user;
        :return:
        """
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)
        self.main_widget.mainlayout.rightlayout.secondlayout.icon01.setVisible(False)

    def order_work8(self, img_qrcode):
        # print('order_work8 begins')
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
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('reconenction of the weigher2 is successful at order_work8.')
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at order_work8.')
        # print('order_work8 ends')

    def user_tracking_work9(self):
        """
        The primary user is gone therefore the account thread should work again;
        """
        # print('user_tracking_work9 begins')
        self.user_id = 'invalid'
        self.new_user_flag = True
        self.main_widget.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.main_widget.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(
            self.main_widget.mainlayout.rightlayout.firstlayout.imgDefault)
        self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
            self.main_widget.mainlayout.rightlayout.secondlayout)
        self.main_widget.mainlayout.rightlayout.secondlayout.icon01.setVisible(False)
        self.thread5.start()
        # print('the status of account thread currently is %s'% self.thread5.isRunning())
        # print('user_tracking_work9 ends')

    def ml_gesture_work10(self):
        """
        Keyword Error might happens if ml_gesture_work10 starts and the user id or the order number are none;
        the information about the user id and the order number might be out of date;
        """
        self.mylogging.logger.info('ml_gesture_work10 begins')
        # print('ml_gesture_work10 begins')
        if self.user_id == 'invalid' or self.order_number == 'invalid':
            self.mylogging.logger.info('ml_gesture_work10 (end): the user id or the order number is invalid.')
            # print('ml_gesture_work10 (end): the user id or the order number is invalid.')
            while self.thread0_0.isRunning():
                self.mylogging.logger.info('waiting for ml_item thread to stops and then restarting it.')
                time.sleep(0.5)  # the account thread can be in running status (not finished status) at this point.
            self.thread0_0.start()
        else:
            # self.main_widget.mainlayout.rightlayout.secondlayout.movie.stop()
            self.main_widget.mainlayout.rightlayout.secondlayout.icon01.setVisible(False)
            self.thread8.dict01['user_id'] = self.user_id
            self.thread8.dict01['order_no'] = self.order_number
            self.thread8.start()
            self.mylogging.logger.info('ml_gesture_work10 ends: the user id and order number are valid.')
            # print('ml_gesture_work10 ends')

    def websocket_work11(self):
        """My server says that the gesture-pay is successful which indicates the end of such transaction"""
        # print('websocket_work11 begins')
        self.main_frame.stacked_layout.setCurrentWidget(self.end_widget_success)
        self.thread10.dict01['order_no'] = self.order_number
        self.thread10.img_user = copy.deepcopy(self.user_img)  # I am afraid the network problem and it need to resend them.
        self.thread10.img_items = copy.deepcopy(self.items_img)
        self.thread10.img_gesture = copy.deepcopy(self.gesture_img)
        self.thread10.start()  # What if the image-upload thread still runs since the network problem in last purchase?
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file05)
        self.media_player.player.play()
        # print('websocket_work11 ends')

    def gesture_pay_work12(self):
        """My server says that the gesture-pay is failed since one user only can pay 5 times everyday"""
        # print('gesture_pay_work12 begins')
        self.main_frame.stacked_layout.setCurrentWidget(self.end_widget_error)
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        # print('gesture_pay_work12 ends')

    def websocket_work12(self):
        """My server says that the gesture-pay is failed since the account value is not enough;
        """
        # print('websocket_work12 begins')
        self.main_frame.stacked_layout.setCurrentWidget(self.end_widget_error)
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        # print('websocket_work12 ends')

    def websocket_work13(self, door_id):
        """My server says opening the specific door."""
        pass

    def account_work14(self, wechatpay_entrust):
        """
        :param wechatpay_entrust: indicating whether the user can show the thumbs-up to finish the payment;;
        :return:
        """
        # print('account_work14 begins')
        if wechatpay_entrust == 0:
            self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
                self.main_widget.mainlayout.rightlayout.secondlayout_2ndWidget)
        elif wechatpay_entrust == 1:
            self.main_widget.mainlayout.rightlayout.secondlayout_main.setCurrentWidget(
                self.main_widget.mainlayout.rightlayout.secondlayout)
        # print('account_work14 ends')

    def ml_gesture_work15a(self, gesture_img, datetime):
        """
        This function is executed after the ML model for gesture detection is finished.
        :param gesture_img: the thumbs-up image
        :param datetime: the datetime.datetime class
        :return:
        """
        cv2.imwrite(os.path.join(self.working_images_path, '%s_gesture.jpg' % datetime.strftime('%Y%m%d_%Hh%Mm%Ss')), gesture_img)
        self.gesture_img = gesture_img
        self.gesture_time = datetime

    def ml_item_work15b(self, items_img, datetime):
        """
        This function is executed after the ML model for item detection is finished.
        :param items_img: the items image
        :param datetime: the datetime.datetime class
        :return:
        """
        if self.thread0_0.isRunning():
            cv2.imwrite(os.path.join(self.working_images_path, '%s_items.jpg' % datetime.strftime('%Y%m%d_%Hh%Mm%Ss')), items_img)
            self.items_img = items_img
            self.items_time = datetime

    def account_work15c(self, user_img, datetime):
        """
        This function is executed after the successful user detection.
        :param user_img: the user image
        :param datetime: the datetime.datetime class
        :return:
        """
        if self.thread0_0.isRunning():
            cv2.imwrite(os.path.join(self.working_images_path, '%s_user.jpg' % datetime.strftime('%Y%m%d_%Hh%Mm%Ss')), user_img)
            self.user_img = user_img
            self.user_time = datetime

    def account_error01(self):
        """
        The account thread should restart since the network problem(timeout problem);
        """
        self.thread5.start()

    def gesture_pay_error02(self):
        """
        Timeout error happens in the gesture-order thread, the gesture order thread should run again;
        """
        self.thread8.dict01['user_id'] = self.user_id
        self.thread8.dict01['order_no'] = self.order_number
        self.thread8.start()

    def image_upload_error03(self):
        """
        Error might happen in the Image_upload thread.
        :return: 
        """
        self.thread10.start()

    def order_error04(self):
        """
        Error might happen in the QRcode thread.
        In normal situation,
        :return:
        """
        self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        self.order_number = 'invalid'
        self.new_order_flag = True
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            # self.mylogging.logger.info('reconenction of the weigher2 is successful at order_error04.')
            pass
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at order_error04.')

    def sql_error05(self):
        """
        Error might happen in the SQL thread.
        For instance, the mysql connection is closed since there is no action to query the database over 8 hours.
        """
        self.main_widget.mainlayout.rightlayout.thirdlayout.clear()
        self.order_number = 'invalid'
        self.new_order_flag = True
        # self.thread3.start()
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            # self.mylogging.logger.info('reconenction of the weigher2 is successful at sql_error05.')
            pass
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at sql_error05.')

    def closeEvent(self, event):
        """
        This has unexpected outcome and the reason is not been discovered yet.
        """
        if self.myconfig.data['operating_mode']['isdebug'] == '1':
            dialog_status = self.camera_dialog.close()
            self.mylogging.logger.info('The camera item dialog closed with %s' % dialog_status)
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread.
        # self.thread2.status = False
        # self.thread3.status = False
        self.weigher1.serial.close()
        self.weigher2.serial.close()
        self.thread5.status = False
        self.thread7.status = False
        self.thread8.status = False
        self.thread4.conn.close()
        self.thread0_0.status = False
        self.main_widget.mainlayout.rightlayout.secondlayout.capture0.release()
        self.capture1.release()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = PaymentSystem()
    mainwindow.show()
    sys.exit(app.exec_())

