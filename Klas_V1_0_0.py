# -*- coding: utf-8 -*-
"""
Payment System
author: hobin
"""
import copy
import cv2
import sys
import time

import os

import gc
from PyQt5.QtCore import QTimer, QThread, QIODevice, QObject
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout
# -----------------------------------------------------------------------------------------------
from qtMediaPlayer import MyMediaPlayer
from CommonView import MainWindow
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
from EndLayout import EndLayout
from CameraLayout import CameraDialog
from CameraThread import MyThread2_1
from ML_Model import Detection1_2_1, Detection2_3_1_klas
from sqlThread import MyThread3_2_1
from AccountThread import MyThread4_4_2_klas
from QRcodeThread import MyThread5_3
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

class PaymentSystem_klas(QObject):

    def __init__(self, **kwargs):
        super(PaymentSystem_klas, self).__init__()
        # configuration
        self.myconfig = MyConfig1()

        # user guide
        if self.myconfig.data['operating_mode']['need_guide'] == '1':
            a = UserGuide03linux01(cfg_path='Klas2.cfg')
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



        # other UI component
        # This reminder is currently used in sql_work5_klas function.
        self.reminder_weight_wrong_status = False  # True indicates the reminder is visible.
        self.reminder_weight_wrong = ReminderWeight02()

        # media player
        self.media_player = MyMediaPlayer(self)

        # item camera
        self.capture1 = cv2.VideoCapture(int(self.myconfig.data['cam_item']['cam_num']))
        self.capture1.set(3, int(self.myconfig.data['cam_item']['width']))  # 3 indicates the width;
        self.capture1.set(4, int(self.myconfig.data['cam_item']['height']))  # 4 indicates the height;

        # for switching the standby layout and main layout;
        self.weigher1 = Weigher1_1(**self.myconfig.data['weigher'])
        self.weigher1.detect_plus.connect(self.weigher1_work1_klas)

        # showing the camera frame for items
        if self.myconfig.data['operating_mode']['isdebug'] == '1':
            self.camera_dialog = CameraDialog(camera_object=self.capture1)
            self.camera_dialog.show()

        # shopping timer
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.shopping_timer_work3_klas)

        # weigher 2
        self.record_weight = 0.0
        self.weigher2 = Weigher2(**self.myconfig.data['weigher'])
        self.weigher2.empty.connect(self.weigher2_work4b_klas)
        self.weigher2.detect_changed.connect(self.weigher2_work4c_klas)

        # thread4 is about the SQL statement
        self.thread4 = MyThread3_2_1(parent=self, **self.myconfig.data['db'])
        self.thread4.finished.connect(self.sql_work5_klas)
        self.thread4.error_connection.connect(self.sql_error05)

        # thread5 is about the account detection
        self.user_name = None
        self.user_portrait = QImage()
        self.thread5 = MyThread4_4_2_klas(parent=self, **self.myconfig.data['account'])
        self.thread5.user_info_success.connect(self.account_work6_klas)
        self.thread5.upload_img.connect(self.account_work15_klas)
        self.thread5.timeout_http.connect(self.account_error01)

        # thread6 is about the QR code thread
        self.thread6 = MyThread5_3(parent=self, **self.myconfig.data['order'])
        self.thread6.finished.connect(self.order_work8_klas)
        self.thread6.timeout_network.connect(self.order_error04)

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
        self.reminder_other_error_status = False
        self.thread0_1 = Detection1_2_1(camera_object=self.capture1, parent=self, **self.myconfig.data['ml_item'])
        self.thread0_1.detected.connect(self.ml_item_work2)
        self.thread0_1.upload_img.connect(self.ml_item_work15b)

        # ML Model for hand detection
        self.new_user_flag = True
        self.new_order_flag = True
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.thread0_0 = Detection2_3_1_klas(parent=self, **self.myconfig.data['ml_hand'])
        # self.thread0_0.setPriority(QThread.HighPriority)
        self.thread0_0.detected.connect(self.ml_gesture_work10_klas)
        self.thread0_0.upload_image.connect(self.ml_gesture_work15a)

        # layout management
        self.main_window = MainWindow()

        #
        del self.image_pay_success
        del self.image_pay_error
        self.mylogging.logger.info('------------------Klas is ready to work------------------------------------')
        # self.thread2.start()
        if self.weigher1.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('the first connection of the weigher1 is successful.')
        else:
            self.mylogging.logger.info('the first connection of the weigher1 is failed.')


    def weigher1_work1_klas(self):
        """
        Aim: switching the layout from standby to main;
        Requirement:
        stopping the CameraThread and starting the timer
        Optimization:
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        But you don't know which one is working.
        """
        self.main_window.toSettlement()
        self.mylogging.logger.info(
            '--------------------------------Next transaction begins!---------------------------------********')
        self.timer1.start(24*60*1000)  # unit: millisecond;
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('reconenction of the weigher2 is successful at weigher1_work1_klas.')
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at weigher1_work1_klas.')
        self.thread0_0.start()

    def ml_item_work2(self, result_detected):
        """
        The ML_item model says that the current result is not empty and it is different from the last result (Detection1_2_2 class).
        After the result of detection is done, we run the thread4 to use the result and query the database;
        After the querying, thread4 initiate the sql_work5_klas() to refresh the GUI;
        :param result_detected: a list;
        :return: a list of detected product;
        """
        self.thread4.detected_result = result_detected
        self.thread4.start()

    def shopping_timer_work3_klas(self):
        """
        when there is no action, returns to the standby layout;
        It is executed by a QTimer;
        """
        self.mylogging.logger.info('shopping_timer_work3_klas begins')
        self.main_window.toWelcome()
        self.mylogging.logger.info('shopping_timer_work3_klas: Klas is back to the standby layout.')
        self.timer1.stop()
        self.weigher2.serial.close()
        self.weigher1.record_value = self.weigher2.record_value
        self.weigher2.record_value = 0.0
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.thread0_1.last_result = []  # If you do not refresh it, the last detected result comes from the last transaction.
        gc.collect()
        self.mylogging.logger.info('--------------------------------Clear, Ready for next transaction---------------------------------********')
        # print('--------------------------------Clear, Ready for next transaction---------------------------------')
        # self.thread2.start()  # Ideally, this is not the first time to starting this thread! It is a re-start!
        if self.weigher1.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('connection of the weigher1 is successful at shopping_timer_work3_klas.')
        else:
            self.mylogging.logger.info('connection of the weigher1 is failed at shopping_timer_work3_klas.')

    def weigher2_work4b_klas(self):
        """
        This function is initialized by the empty signal of self.weigher2;
        This function is to clear the information about the order since the current weight is zero.
        The self.weigher2 still works when this function is executed.
        """
        self.main_window.cleanCommodity()
        self.main_window.setSumPrice('0.0')
        self.order_number = 'invalid'
        self.new_order_flag = True
        self.thread0_1.last_result = []  # the communication between weigher and the ML Model for the ShoppingList Layout.
        self.reminder_weight_wrong.label1.setText('The current weight is 0.')
        if not self.reminder_weight_wrong_status:
            self.reminder_weight_wrong.setVisible(True)
            self.reminder_weight_wrong_status = True

    def weigher2_work4c_klas(self, record_weight):
        """
        This function is initialized by the 'detect_changed' signal of self.weigher2;
        """
        self.new_order_flag = True
        if self.reminder_other_error_status:
            self.main_window.hideErrorInfo()
            self.reminder_other_error_status = False
        self.mylogging.logger.info(
            '------------------------------start a new ML calculation---------------------------------------------')
        self.record_weight = record_weight
        # print('weigher2_work4c_klas begins')
        self.thread0_1.start()
        # print('weigher2_work4c_klas ends')

    def sql_work5_klas(self, result_sql):
        """
        To refresh my ShoppingList widget
        :param result_sql: a list of tuples;
        :return:
        """
        self.mylogging.logger.info('sql_work5_klas begins')

        # with verification
        weight_range = verifyWeight2(result_sql)
        if weight_range[0] <= self.record_weight <= weight_range[1]:
            if self.reminder_weight_wrong_status:
                self.reminder_weight_wrong.setHidden(True)
                self.reminder_weight_wrong_status = False
            # Be careful the result_sql might be empty.
            if len(result_sql) == 0:
                self.mylogging.logger.info('sql_work5_klas detects no item.')
                self.main_window.cleanCommodity()
                self.main_window.setSumPrice('0')
            elif len(result_sql) >4:
                self.mylogging.logger.info('sql_work5_klas detects more than 4 items')
                self.main_window.cleanCommodity()
                self.main_window.setSumPrice('0')
                self.main_window.showErrorInfo(3)  # You need to hide it by yourself
                self.reminder_other_error_status = True
            else:
                self.mylogging.logger.info('sql_work5_klas starts to add items')
                sum = 0.0
                for index, item in enumerate(result_sql):
                    self.main_window.addCommodity(picid=index+1, name=item[0], image=str(item[3]), price=item[2])
                    sum = sum + float(item[2])
                self.main_window.setSumPrice('%.2f' %sum)
                self.mylogging.logger.info('sql_work5_klas ends to add items')
                self.thread6.dict01['buy_skuids'] = ','.join([str(product[3]) for product in result_sql])
                self.thread6.start()
        else:
            self.mylogging.logger.info('sql_work5_klas: wrong verification of weight')
            # if the order number exists, set them to the default situation.
            self.thread0_1.last_result = []
            if self.order_number != 'invalid':
                self.main_window.cleanCommodity()
                self.order_number = 'invalid'
            # reminding the customer to place those item again
            self.reminder_weight_wrong.label1.setText('The record value is %s and it is not in range (%.2f,%.2f)'
                                                      % (self.record_weight, weight_range[0],weight_range[1]))
            if not self.reminder_weight_wrong_status:
                self.reminder_weight_wrong.setVisible(True)
                self.reminder_weight_wrong_status = True
            # self.thread3.start()
            if self.weigher2.serial.open(QIODevice.ReadOnly):
                # self.mylogging.logger.info('reconenction of the weigher2 is successful at sql_work5_klas.')
                pass
            else:
                self.mylogging.logger.info('reconenction of the weigher2 is failed at sql_work5_klas.')

        self.mylogging.logger.info('sql_work5_klas ends')

    def account_work6_klas(self, user_name, user_img, wechat_entrust, user_face):
        """
        to refresh the information about the account only if detection successes;
        :argument user_name: the name of the wechat account
        :argument user_img: the user portrait of the wechat account
        :argument wechat_entrust: 0 indicates that the gesture-pay is not allowed. 1 indicates it is allowed.
        :argument user_face: the user face given by the account thread; the data type is ndarray;
        :return:
        """
        self.mylogging.logger.info('account_work6_klas begins.')
        self.user_name = user_name
        self.user_portrait.loadFromData(user_img)
        img1 = cv2.cvtColor(user_face, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
        height, width, channel = img1.shape  # width=640, height=480
        bytes_per_line = 3 * width
        img2 = QImage(img1.data, width, height, bytes_per_line, QImage.Format_RGB888)
        if wechat_entrust == 1:
            self.mylogging.logger.info('account_work6_klas detects that the user can show gesture to finish the payment.')
            self.main_window.toPayingView(img2)
            self.user_id = self.thread5.dict02['data']['user_id']
            if self.user_id == 'invalid' or self.order_number == 'invalid':
                self.mylogging.logger.info('account_work6_klas (end): the user id or the order number is invalid.')
                self.main_window.toSettlement()
                self.thread0_0.order_number = 'invalid'
                self.thread0_0.start()
            else:
                if self.order_number == self.thread0_0.order_number:
                    self.thread8.dict01['user_id'] = self.user_id
                    self.thread8.dict01['order_no'] = self.order_number
                    self.mylogging.logger.info('account_work6_klas (end): order is ready to be submitted.')
                    self.thread8.start()
                else:
                    self.mylogging.logger.info('account_work6_klas (end): the current order number is different from the order number recorded by the gesture ML Model.')
                    self.main_window.toSettlement()
                    self.thread0_0.order_number = 'invalid'
                    self.thread0_0.start()
        else:
            self.mylogging.logger.info(
                'account_work6_klas detects that the user can not show gesture.')
            self.main_window.toPayingView(img2)
            self.main_window.toRegisterView()

    def order_work8_klas(self, post_order_success):
        """
        :param post_order_success: True indicates the new order is recorded by the server;
        :return:
        """
        # print('order_work8_klas begins')
        if post_order_success:
            self.order_number = self.thread6.dict02['data']['order_no']
            self.new_order_flag = False
        else:
            self.order_number = 'invalid'
            self.new_order_flag = True
        if self.weigher2.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('reconenction of the weigher2 is successful at order_work8_klas.')
        else:
            self.mylogging.logger.info('reconenction of the weigher2 is failed at order_work8_klas.')
        # print('order_work8_klas ends')

    def ml_gesture_work10_klas(self):
        """
        The system successfully detects the thumbs-up and next task is to detect account.
        :return:
        """
        self.thread5.start()

    def websocket_work11(self):
        """My server says that the gesture-pay is successful which indicates the end of such transaction"""
        # print('websocket_work11 begins')
        self.main_window.toPaySuccessView(name=self.user_name, image=self.user_portrait)
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
        self.main_window.toPayFailView(name=self.user_name, image=self.user_portrait)
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        # print('gesture_pay_work12 ends')

    def websocket_work12(self):
        """My server says that the gesture-pay is failed since the account value is not enough;
        """
        # print('websocket_work12 begins')
        self.main_window.toPayFailView(name=self.user_name, image=self.user_portrait)
        self.timer1.start(8000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        # print('websocket_work12 ends')

    def websocket_work13(self, door_id):
        """My server says opening the specific door."""
        pass

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

    def account_work15_klas(self, user_img, datetime):
        """
        This function is executed after the successful user detection.
        :param user_img: the user image
        :param datetime: the datetime.datetime class
        :return:
        """
        cv2.imwrite(os.path.join(self.working_images_path, '%s_user.jpg' % datetime.strftime('%Y%m%d_%Hh%Mm%Ss')),
                    user_img)
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
    mainwindow = PaymentSystem_klas()
    # mainwindow.show()
    sys.exit(app.exec_())

