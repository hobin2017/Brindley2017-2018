# -*- coding: utf-8 -*-
"""
Payment System
Compared with Klas_Singtel_V1_1_0, the getting_ip function is changed by using socket.
author: hobin;
email = '627227669@qq.com';
"""
import copy
import socket

import cv2
import sys
import time

import os

import gc

import qrcode
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QTimer, QThread, QIODevice, QObject, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtNetwork import QHostInfo, QAbstractSocket
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout, QDialog, QLabel
# -----------------------------------------------------------------------------------------------
from CameraThread import MyCameraThread1_2
from qtMediaPlayer import MyMediaPlayer
from CameraLayout import CameraDialog
from ML_Model import Detection1_2_1, Detection2_3_2_klas_singtel, Detection1_multi_model_1
from ML_Model import Detection1_simulation, Detection2_simulation_singtel
from sqlThread import MyThread3_2_3
from AccountThread import MyThread4_0_1_3_1
from QRcodeThread import MyThread5_3_1_1
from GesturePayThread import MyThread7_1_1
from WebSocketClientThread import MyThread8_3
from ImageUploadThread import MyThread9_1_2
from Weigher import Weigher3_1, Weigher3_2
from ConfiguringModule import MyConfig1
from LoggingModule import MyLogging1
from StatisticsMethod import verifyWeight2_2
from Selfcheck import necessaryCheck_linux
from ReminderLayout import ReminderWeight02
from UserGuide import UserGuide03_1linux01
from AllLayout_Singtel import SingtelWindow01
from LoadingLayout_Singtel import LoadingLayout01
from DoorController import DoorController01
from DatabaseUpdateThread import skuDownloadThread01, skuDownloadFinishedThread01


class PaymentSystem_klas(QObject):

    def __init__(self, **kwargs):
        super(PaymentSystem_klas, self).__init__()
        # configuration
        self.myconfig = MyConfig1(cfg_path='Klas2_Singtel.cfg')

        # user guide
        if self.myconfig.data['operating_mode']['need_guide'] == '1':
            a = UserGuide03_1linux01(cfg_path='Klas2_Singtel.cfg')
            reply = a.exec()
            if reply != 0:
                sys.exit('Error happens in user guide, please start again')
            self.myconfig = MyConfig1(cfg_path='Klas2_Singtel.cfg')  # to refresh the configuration.

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
        icon_path = os.path.join(self.image_path, 'payment.png')
        self.image_pay_success = os.path.join(self.image_path, 'pay_success.png')
        self.image_pay_error = os.path.join(self.image_path, 'pay_error.png')
        # the expected outcome is like './working_images';
        self.working_images_path = os.path.join(self.project_path, 'working_images')
        if not os.path.exists(self.working_images_path):
            os.makedirs(self.working_images_path)
        self.working_images_original_path = os.path.join(self.project_path, 'working_images_original')
        if not os.path.exists(self.working_images_original_path):
            os.makedirs(self.working_images_original_path)
        # the expected outcome is like './item_images';
        self.item_images_path = os.path.join(self.project_path, 'item_images')
        if not os.path.exists(self.item_images_path):
            os.makedirs(self.item_images_path)


        # other UI component
        # This reminder is currently used in sql_work5_klas function.
        self.reminder_weight_wrong_status = False  # True indicates the reminder is visible.
        self.reminder_weight_wrong = ReminderWeight02()

        # media player
        self.media_player = MyMediaPlayer(self)

        # item camera
        if self.myconfig.data['operating_mode']['cam_path_used'] == '1':
            self.capture1 = cv2.VideoCapture(self.myconfig.data['cam_item']['cam_path'])
        else:
            self.capture1 = cv2.VideoCapture(int(self.myconfig.data['cam_item']['cam_num']))
        self.capture1.set(3, int(self.myconfig.data['cam_item']['width']))  # 3 indicates the width;
        self.capture1.set(4, int(self.myconfig.data['cam_item']['height']))  # 4 indicates the height;

        # item camera 2
        if self.myconfig.data['cam_item2']['is_used'] == '1':
            if self.myconfig.data['operating_mode']['cam_path_used'] == '1':
                self.capture3 = cv2.VideoCapture(self.myconfig.data['cam_item2']['cam_path'])
            else:
                self.capture3 = cv2.VideoCapture(int(self.myconfig.data['cam_item2']['cam_num']))
            self.capture3.set(3, int(self.myconfig.data['cam_item2']['width']))  # 3 indicates the width;
            self.capture3.set(4, int(self.myconfig.data['cam_item2']['height']))  # 4 indicates the height;
        else:
            if self.myconfig.data['ml_item']['multi_model_item'] == '1':
                sys.exit('Configuration problem: the camera used for the multi-camera ML Model is missing.')

        # for switching the standby layout and main layout;
        # the weigher1 and weigher2 become weigher3;

        # showing the camera frame for items
        if self.myconfig.data['operating_mode']['show_cam_item'] == '1':
            self.camera_dialog = CameraDialog(camera_object=self.capture1)
            self.camera_dialog.show()

        # get the current ip address for
        self.getting_ip_address()  # the ip is stored at the 'self.current_ip_address' variable.
        
        # loading the item images to memory
        self.item_images_dict = {}
        self.loading_images2memory()

        # shopping timer
        self.shopping_time_counter = 100 * 1000  # unit: ms
        self.accelerate_to_standby_counter = 2.5 * 1000  # unit: ms
        self.timer1 = QTimer(self)
        self.timer1.setSingleShot(True)
        self.timer1.timeout.connect(self.shopping_timer_work3_klas)

        # timer for showing the pay successes view despite the failure of eliminating magnetic
        self.timer3_not_timeout_status = True
        self.magnetic_signal_not_received = True
        self.timer3 = QTimer(self)
        self.timer3.setSingleShot(True)
        self.timer3.timeout.connect(self.door_controller_work24)

        # timer for the local database update
        self.database_update_status = True
        self.database_update_timer = QTimer(self)
        self.database_update_timer.timeout.connect(self.database_update_work26)
        self.database_update_timer.start(5*60*1000)

        # weigher 2
        self.record_weight = 0.0
        if self.myconfig.data['weigher']['unit'] == 'g':
            self.weigher = Weigher3_2(**self.myconfig.data['weigher'])
            self.weigher.detect_plus.connect(self.weigher1_work1_klas)
            self.weigher.empty.connect(self.weigher2_work4b_klas)
            self.weigher.detect_changed.connect(self.weigher2_work4c_klas)
            self.weigher.to_standby.connect(self.weigher_work19_klas)
        else:
            self.weigher = Weigher3_1(**self.myconfig.data['weigher'])
            self.weigher.detect_plus.connect(self.weigher1_work1_klas)
            self.weigher.empty.connect(self.weigher2_work4b_klas)
            self.weigher.detect_changed.connect(self.weigher2_work4c_klas)
            self.weigher.to_standby.connect(self.weigher_work19_klas)

        # thread4 is about the SQL statement
        self.error_try_times_sql = 0
        self.thread4 = MyThread3_2_3(parent=self, **self.myconfig.data['db'])
        self.thread4.finished.connect(self.sql_work5_klas)
        self.thread4.error_connection.connect(self.sql_error05)
        self.thread4.error_algorithm.connect(self.sql_error06)

        # thread5 is about the account detection
        self.user_name = None
        self.user_portrait = QImage()
        self.error_try_times_account = 0
        self.failed_detection_local_counter = 0
        self.failed_detection_multiple_counter = 0
        self.thread5 = MyThread4_0_1_3_1(parent=self, client_ip=self.current_ip_address, **self.myconfig.data['account'])
        self.thread5.freezing_gesture.connect(self.account_work16_klas, type=Qt.BlockingQueuedConnection)
        self.thread5.user_info_success.connect(self.account_work6_klas)
        self.thread5.upload_img.connect(self.account_work15_klas)
        self.thread5.timeout_http.connect(self.account_error01)
        self.thread5.connection_error.connect(self.account_error01)
        self.thread5.error.connect(self.account_error01)
        self.thread5.failed_detection_web_klas.connect(self.account_work7_klas)
        self.thread5.failed_detection_local.connect(self.account_work17_klas)
        self.thread5.failed_detection_multiple.connect(self.account_work18_klas)

        # thread6 is about the QR code thread
        self.icon = Image.open(icon_path)
        self.icon_w, self.icon_h = self.icon.size
        self.order_link = None
        self.thread6 = MyThread5_3_1_1(parent=self, client_ip=self.current_ip_address, **self.myconfig.data['order'])
        self.thread6.finished.connect(self.order_work8_klas02)
        self.thread6.timeout_network.connect(self.order_error04)
        self.thread6.error.connect(self.order_error07)

        # thread8 is about the gesture-pay thread
        self.error_try_times_gesture_pay = 0
        self.thread8 = MyThread7_1_1(client_ip=self.current_ip_address, **self.myconfig.data['gesture_pay'])
        self.thread8.finished_error.connect(self.gesture_pay_work12)
        self.thread8.timeout_http.connect(self.gesture_pay_error02)
        self.thread8.connection_error.connect(self.gesture_pay_error02)
        self.thread8.error.connect(self.gesture_pay_error02)
        self.thread8.network_error.connect(self.gesture_pay_error08)
        # self.thread8.order_success.connect(self.gesture_pay_work21)

        # thread9 is about the websocket thread
        self.transaction_not_end_status = True
        self.pay_clear_by_gesture = True  # just used for upload image
        self.thread9 = MyThread8_3(**self.myconfig.data['websocket'])
        self.thread9.payclear_success.connect(self.websocket_work11_klas)
        self.thread9.payclear_failure.connect(self.websocket_work12)
        self.thread9.opendoor.connect(self.websocket_work13)
        self.thread9.payclear_success_code.connect(self.websocket_work25)
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
        self.error_try_times_image_upload = 0
        self.success_order_number = None
        self.thread10 = MyThread9_1_2(client_ip=self.current_ip_address, **self.myconfig.data['image_upload'])
        self.thread10.error.connect(self.image_upload_error03)

        # thread12 is about the update of local database
        self.thread12 = skuDownloadThread01(**self.myconfig.data['update_sku_dwonload'])
        self.thread12.finish_with_sku.connect(self.database_update_work27)
        self.thread12.update_images_dict.connect(self.database_update_work28, type=Qt.QueuedConnection)

        #
        self.thread13 = skuDownloadFinishedThread01(**self.myconfig.data['update_sku_dwonload_finished'])

        # ML Model for item detection
        if self.myconfig.data['simulation_item']['is_used'] == '1':
            self.thread0_1 = Detection1_simulation(camera_object=self.capture1, **self.myconfig.data['simulation_item'])
            self.thread0_1.detected.connect(self.ml_item_work2)
            self.thread0_1.upload_img.connect(self.ml_item_work15b)
        elif self.myconfig.data['ml_item']['multi_model_item'] == '1':
            self.thread0_1 = Detection1_multi_model_1(camera_object=self.capture1, camera_object_2= self.capture3,
                                                     model2_used=True, parent=self, **self.myconfig.data['ml_item'])
            self.thread0_1.detected.connect(self.ml_item_work2)
            self.thread0_1.upload_img.connect(self.ml_item_work15b)
        else:
            self.thread0_1 = Detection1_2_1(camera_object=self.capture1, parent=self, **self.myconfig.data['ml_item'])
            self.thread0_1.detected.connect(self.ml_item_work2)
            self.thread0_1.upload_img.connect(self.ml_item_work15b)

        # ML Model for hand detection
        self.new_user_flag = True
        self.new_order_flag = True
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.gesture_frame_location = {'x':0,'y':0,'length':0}
        self.gesture_frame_frozen_status = False
        if self.myconfig.data['simulation_hand']['is_used'] == '1':
            self.thread0_0 = Detection2_simulation_singtel(parent=self, **self.myconfig.data['simulation_hand'])
            self.thread0_0.detected_gesture_info.connect(self.ml_gesture_work10_klas02)
            self.thread0_0.upload_image.connect(self.ml_gesture_work15a)
        else:
            self.thread0_0 = Detection2_3_2_klas_singtel(parent=self, **self.myconfig.data['ml_hand'])
            self.thread0_0.detected_gesture_info.connect(self.ml_gesture_work10_klas02)
            self.thread0_0.upload_image.connect(self.ml_gesture_work15a)

        # layout widgets
        self.main_window_error_status = False
        if self.myconfig.data['operating_mode']['cam_path_used'] == '1':
            cam_user = self.myconfig.data['cam_user']['cam_path']
        else:
            cam_user = int(self.myconfig.data['cam_user']['cam_num'])
        self.main_window = SingtelWindow01(parent=self, **self.myconfig.data['layout'])
        self.main_window.preprocess_work()
        self.user_capture01 = cv2.VideoCapture(cam_user)
        self.user_capture01.set(3, int(self.myconfig.data['cam_user']['width']))
        self.user_capture01.set(4, int(self.myconfig.data['cam_user']['height']))
        self.cam_thread = MyCameraThread1_2(camera_object=self.user_capture01)
        self.cam_thread.update.connect(self.main_window.mainlayout_right_widget01.camera_widget.refresh)


        # door controller
        self.door_controller = DoorController01(**self.myconfig.data['door_controller'])
        self.door_controller.outOpenDooSuccessByUser.connect(self.door_controller_work22)
        self.door_controller.outOpenDooSuccess.connect(self.door_controller_work23)
        self.door_controller.degaussSuccess.connect(self.door_controller_work24)

        #
        del self.image_pay_success
        del self.image_pay_error
        self.mylogging.logger.info('------------------Klas is ready to work------------------------------------')
        self.cam_thread.start()
        if self.weigher.serial.open(QIODevice.ReadOnly):
            self.mylogging.logger.info('the first connection of the weigher is successful.')
        else:
            self.mylogging.logger.info('the first connection of the weigher is failed.')
            sys.exit('the first connection of the weigher1 is failed.')


    def getting_ip_address(self):
        self.mylogging.logger.info('getting_ip_address starts')
        self.current_ip_address = '0.0.0.0'  # if using None, it might cause the error hash value
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # to get ip by using udp protocal
        try:
            temp_socket.connect(('8.8.8.8', 80))
            self.current_ip_address = temp_socket.getsockname()[0]
        except BaseException:
            self.mylogging.logger.error('error happens in getting_ip_address.', exc_info=True)
        finally:
            temp_socket.close()
        self.mylogging.logger.info('getting_ip_address ends with %s' %self.current_ip_address)
        
    def loading_images2memory(self):
        self.mylogging.logger.info('loading_images2memory starts')
        image_name_list = [item for item in os.listdir(self.item_images_path) if os.path.splitext(item)[1] == '.jpg']
        for image_name in image_name_list:
            dict_key = os.path.splitext(image_name)[0]  # the value should be the same as the sku_id
            self.item_images_dict[dict_key] = QPixmap(os.path.join(self.item_images_path, image_name))
        self.mylogging.logger.info('loading_images2memory ends')

    def weigher1_work1_klas(self):
        """
        Aim: switching the layout from standby to main;
        Requirement:
        stopping the CameraThread and starting the timer
        Optimization:
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        But you don't know which one is working.
        """
        self.mylogging.logger.info('weigher1_work1_klas begins')
        if self.gesture_frame_frozen_status:
            # adding this since the account thread result might be no well matched user and you freeze the frame.
            self.main_window.stopHandGif()  # the main layout is restored manually
            self.gesture_frame_frozen_status = False
        self.main_window.toSettlement()
        self.mylogging.logger.info(
            '--------------------------------Next transaction begins!---------------------------------********')
        self.timer1.start(self.shopping_time_counter) # unit: millisecond, 24 hrs = 24*60*60*1000, 3 mins = 180000
        # If self.weigher.record_value = 0.0 is omitted, the ml item model actually does not starts when the standby layout is switched to the main layout;
        self.weigher.record_value = 0.0
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        self.thread0_0.start()
        self.mylogging.logger.info('weigher1_work1_klas ends')

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
        if self.myconfig.data['operating_mode']['weight_error'] == '1':
            self.reminder_weight_wrong.setHidden(True)
            self.reminder_weight_wrong_status = False
        if self.myconfig.data['operating_mode']['normal_error'] == '1':
            self.main_window.hideErrorInfo()
            self.main_window_error_status = False

        self.main_window.toWelcome()
        self.mylogging.logger.info('shopping_timer_work3_klas: Klas is back to the standby layout.')
        self.thread0_0.status = False
        self.timer1.stop()
        try:
            self.weigher.serial.readyRead.disconnect()
        except TypeError:
            pass
        # self.weigher.record_value = 0.0  # You don't need to clear the record since the costumer does not take items away imediatly;
        self.transaction_not_end_status = True
        self.success_order_number = None
        self.order_link = None
        self.user_name = None
        self.user_portrait = QImage()
        self.thread0_0.frame = None
        self.thread5.frame = None
        self.user_id = 'invalid'
        self.order_number = 'invalid'
        self.new_order_flag = True
        self.new_user_flag = True
        self.mylogging.logger.info('shopping_timer_work3_klas: ends to clear the order and user information')
        self.thread0_1.last_result = []  # If you do not refresh it, the last detected result comes from the last transaction.
        self.failed_detection_local_counter = 0
        self.error_try_times_account = 0
        self.error_try_times_gesture_pay = 0
        self.error_try_times_image_upload = 0
        self.error_try_times_sql = 0
        if self.database_update_status:
            self.database_update_status = False
            self.thread12.start()
        gc.collect()
        time.sleep(2)
        self.thread0_0.status = False
        self.mylogging.logger.info('shopping_timer_work3_klas ends')
        self.mylogging.logger.info('--------------------------------Clear, Ready for next transaction---------------------------------********')

        self.weigher.serial.readyRead.connect(self.weigher.acceptData_standby)

    def weigher2_work4b_klas(self):
        """
        This function is initialized by the empty signal of self.weigher2;
        This function is to clear the information about the order since the current weight is zero.
        The self.weigher2 still works when this function is executed.
        """
        self.mylogging.logger.info('weigher2_work4b_klas begins')
        self.main_window.cleanCommodity()
        self.main_window.setSumPrice('0.0')
        self.order_number = 'invalid'
        self.new_order_flag = True
        self.thread0_1.last_result = []  # the communication between weigher and the ML Model for the ShoppingList Layout.
        self.reminder_weight_wrong.label1.setText('The current weight is 0.')
        if not self.reminder_weight_wrong_status and self.myconfig.data['operating_mode']['weight_error'] == '1':
            self.reminder_weight_wrong.setVisible(True)
            self.reminder_weight_wrong_status = True
        if self.main_window_error_status and self.myconfig.data['operating_mode']['normal_error'] == '1':
            self.main_window.hideErrorInfo()
            self.main_window_error_status = False
        if self.timer1.isActive() and self.transaction_not_end_status:
            self.timer1.start(self.accelerate_to_standby_counter)
        self.mylogging.logger.info('weigher2_work4b_klas ends')

    def weigher2_work4c_klas(self, record_weight):
        """
        This function is initialized by the 'detect_changed' signal of self.weigher2;
        """
        self.new_order_flag = True
        if self.main_window_error_status and self.myconfig.data['operating_mode']['normal_error'] == '1':
            self.main_window.hideErrorInfo()
            self.main_window_error_status = False
        if self.timer1.isActive() and self.transaction_not_end_status:
            self.timer1.start(self.shopping_time_counter)
        # self.media_player.player.setMedia(self.media_player.file06)
        # self.media_player.player.play()
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
        self.main_window.cleanCommodity()
        self.main_window.setSumPrice('0.0')
        # with verification
        weight_range = verifyWeight2_2(result_sql)
        if weight_range[0] <= self.record_weight <= weight_range[1]:
            if self.reminder_weight_wrong_status:
                if self.myconfig.data['operating_mode']['weight_error'] == '1':
                    self.reminder_weight_wrong.setHidden(True)
                    self.reminder_weight_wrong_status = False
                if self.myconfig.data['operating_mode']['normal_error'] == '1':
                    self.main_window.hideErrorInfo()
                    self.main_window_error_status = False
            # Be careful the result_sql might be empty.
            if len(result_sql) == 0:
                self.mylogging.logger.info('sql_work5_klas detects no item.')
                self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
            elif len(result_sql) >4:
                self.mylogging.logger.info('sql_work5_klas detects more than 4 items')
                self.media_player.player.setMedia(self.media_player.file09)
                self.media_player.player.play()
                if self.myconfig.data['operating_mode']['normal_error'] == '1':
                    self.main_window.showErrorInfo(2)  # You need to hide it by yourself
                    self.main_window_error_status = True
                self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
            else:
                self.mylogging.logger.info('sql_work5_klas starts to add items')
                sum = 0.0
                for index, item in enumerate(result_sql):
                    self.main_window.addCommodity(picid=index+1, name=item[0], image=str(item[3]), price=item[2])
                    sum = sum + float(item[2])
                self.main_window.setSumPrice('%.2f' %sum)
                self.mylogging.logger.info('sql_work5_klas ends to add items')
                self.thread6.dict01['weight'] = self.record_weight
                self.thread6.dict01['buy_skuids'] = ','.join([str(product[3]) for product in result_sql])
                self.thread6.start()
        else:
            self.mylogging.logger.info('sql_work5_klas: wrong verification of weight')
            # if the order number exists, set them to the default situation.
            self.thread0_1.last_result = []
            if self.order_number != 'invalid':
                self.order_number = 'invalid'
            media_status = self.media_player.player.mediaStatus()
            if media_status == QMediaPlayer.EndOfMedia or media_status == QMediaPlayer.NoMedia:
                self.media_player.player.setMedia(self.media_player.file10)
                self.media_player.player.play()
            # reminding the customer to place those item again
            self.reminder_weight_wrong.label1.setText('The record value is %s and it is not in range (%.2f,%.2f)'
                                                      % (self.record_weight, weight_range[0],weight_range[1]))
            if not self.reminder_weight_wrong_status:
                if self.myconfig.data['operating_mode']['weight_error'] == '1':
                    self.reminder_weight_wrong.setVisible(True)
                    self.reminder_weight_wrong_status = True

            # Be careful the result_sql might be empty.
            if len(result_sql) == 0:
                self.mylogging.logger.info('sql_work5_klas detects no item.')
                if self.myconfig.data['operating_mode']['normal_error'] == '1':
                    self.main_window.showErrorInfo(0)
                    self.main_window_error_status = True
                self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
            elif len(result_sql) >4:
                self.mylogging.logger.info('sql_work5_klas detects more than 4 items')
                if self.myconfig.data['operating_mode']['normal_error'] == '1':
                    self.main_window.showErrorInfo(2)  # You need to hide it by yourself
                    self.main_window_error_status = True
                self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
            else:
                self.mylogging.logger.info('sql_work5_klas starts to add items')
                sum = 0.0
                for index, item in enumerate(result_sql):
                    self.main_window.addCommodity(picid=index + 1, name=item[0], image=str(item[3]), price=item[2])
                    sum = sum + float(item[2])
                self.main_window.setSumPrice('%.2f' % sum)
                if self.myconfig.data['operating_mode']['normal_error'] == '1':
                    self.main_window.showErrorInfo(0)
                    self.main_window_error_status = True
                self.mylogging.logger.info('sql_work5_klas ends to add items')
            self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)

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
            self.main_window.toPayingView(img2.mirrored(horizontal=True, vertical=False))
            # self.main_window.toPayingView(img2)
            self.user_id = self.thread5.dict02['data']['user_id']
            if self.user_id == 'invalid' or self.order_number == 'invalid':
                self.mylogging.logger.info('account_work6_klas (end): the user id or the order number is invalid.')
                self.main_window.toSettlement()  # the payment layout
                if self.gesture_frame_frozen_status:
                    # although the account thread detects only one user but now something goes wrong.
                    self.main_window.stopHandGif()
                    self.gesture_frame_frozen_status = False
                self.new_order_flag = True
                self.media_player.player.setMedia(self.media_player.file14)
                self.media_player.player.play()
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
                    if self.gesture_frame_frozen_status:
                        # although the account thread detects only one user but now something goes wrong.
                        self.main_window.stopHandGif()
                        self.gesture_frame_frozen_status = False
                    self.new_order_flag = True
                    self.media_player.player.setMedia(self.media_player.file14)
                    self.media_player.player.play()
                    self.thread0_0.order_number = 'invalid'
                    self.thread0_0.start()
        else:
            self.main_window.toPayingView(img2.mirrored(horizontal=True, vertical=False))
            # self.main_window.toPayingView(img2)

            # self.media_player.player.setMedia(self.media_player.file08)
            # self.media_player.player.play()
            # self.timer1.start(30 * 1000)
            try:
                self.weigher.serial.readyRead.disconnect()
            except BaseException:
                pass
            self.weigher.serial.readyRead.connect(self.weigher.acceptData_back_to_standby)
            if self.order_link:
                self.main_window.toRegisterView(image=self.user_portrait, qrimage=self.make_qrcode(self.order_link))
            else:
                self.main_window.toRegisterView()
            self.mylogging.logger.info('account_work6_klas (end) : the user can not show gesture.')

    def account_work7_klas(self, user_face):
        """
        The result given by my server is no well-matched user.
        :return:
        """
        self.mylogging.logger.info('account_work7_klas begins')

        # the first way is to detect again;
        # self.thread0_0.start()
        # if self.gesture_frame_frozen_status:
        #     # adding this since the account thread result might be no well matched user and you freeze the frame.
        #     self.main_window.stopHandGif()
        #     self.gesture_frame_frozen_status = False

        # the second way is show the register page for user or to show the the QR code
        img1 = cv2.cvtColor(user_face, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
        height, width, channel = img1.shape  # width=640, height=480
        bytes_per_line = 3 * width
        img2 = QImage(img1.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.main_window.toPayingView(img2.mirrored(horizontal=True, vertical=False))
        # self.main_window.toPayingView(img2)
        # self.timer1.start(30 * 1000)
        try:
            self.weigher.serial.readyRead.disconnect()
        except BaseException:
            pass
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_back_to_standby)
        if self.order_link:
            self.main_window.toRegisterView(qrimage=self.make_qrcode(self.order_link))
        else:
            self.main_window.toRegisterView()

        self.mylogging.logger.info('account_work7_klas ends')

    def order_work8_klas(self, post_order_success):
        """
        :param post_order_success: True indicates the new order is recorded by the server;
        :return:
        """
        self.mylogging.logger.info('order_work8_klas begins')
        if post_order_success:
            self.order_number = self.thread6.dict02['data']['order_no']
            self.new_order_flag = False
            # self.media_player.player.setMedia(self.media_player.file11)
            # self.media_player.player.play()
        else:
            # when len(self.dict01['buy_skuids']) is equal to 0, the post_order_success will be False;
            self.order_number = 'invalid'
            self.new_order_flag = True
            if self.myconfig.data['operating_mode']['normal_error'] == '1':
                self.main_window.showErrorInfo(0)
                self.main_window_error_status = True
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        self.mylogging.logger.info('order_work8_klas ends')

    def order_work8_klas02(self, order_link):
        """
        :param order_link: if len(thread6.dict01['buy_skuids'])==0, the value of order_link is None; Otherwise, a string which is a link.
        :return:
        """
        self.mylogging.logger.info('order_work8_klas02 begins')
        if order_link:
            self.order_link = order_link
            self.order_number = self.thread6.dict02['data']['order_no']
            self.new_order_flag = False
            # self.media_player.player.setMedia(self.media_player.file11)
            # self.media_player.player.play()
        else:
            # when len(self.dict01['buy_skuids']) is equal to 0, the post_order_success will be False;
            self.order_number = 'invalid'
            self.new_order_flag = True
            if self.myconfig.data['operating_mode']['normal_error'] == '1':
                self.main_window.showErrorInfo(0)
                self.main_window_error_status = True
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        self.mylogging.logger.info('order_work8_klas02 ends')

    def ml_gesture_work10_klas01(self):
        """
        The system successfully detects the thumbs-up and next task is to detect account.
        :return:
        """
        self.thread5.start()

    def ml_gesture_work10_klas02(self, gesture_img, gesture_location):
        """
        The system successfully detects the thumbs-up and next task is to detect account.
        :param gesture_img:
        :param gesture_location: a tuple such as (ymin, xmin, ymax, xmax)
        the original data is like (0.4376579821109772, 0.13899928331375122, 0.9378951191902161, 0.39783698320388794) which is normalized.
        :return:
        """
        self.mylogging.logger.info('ml_gesture_work10_klas02 begins')
        while self.thread0_0.isRunning():
            self.mylogging.logger.info('waits for ml gesture model to stops and then starts account thread.')
            time.sleep(0.5)
        self.gesture_frame_location['x'] = int((gesture_location[1] + gesture_location[3]) * 0.5)
        self.gesture_frame_location['y'] = int((gesture_location[0] + gesture_location[2]) * 0.5)
        self.gesture_frame_location['length'] = int(max(abs(gesture_location[1]-gesture_location[3]), abs(gesture_location[0]-gesture_location[2])))
        # self.mylogging.logger.info('ml_gesture_work10_klas02: the x is %s, the y is %s and the length is %s'
        #                            %(self.gesture_frame_location['x'], self.gesture_frame_location['y'], self.gesture_frame_location['length']))
        self.thread5.frame = gesture_img
        self.thread5.start()
        self.mylogging.logger.info('ml_gesture_work10_klas02 ends')

    def websocket_work11(self):
        """My server says that the gesture-pay is successful which indicates the end of such transaction"""
        self.mylogging.logger.info('websocket_work11 begins')
        self.transaction_not_end_status = False
        self.main_window.toPaySuccessView(name=self.user_name, image=self.user_portrait)
        self.thread10.dict01['order_no'] = self.order_number
        self.thread10.img_user = copy.deepcopy(self.user_img)  # I am afraid the network problem and it need to resend them.
        self.thread10.img_items = copy.deepcopy(self.items_img)
        self.thread10.img_gesture = copy.deepcopy(self.gesture_img)
        self.thread10.start()  # What if the image-upload thread still runs since the network problem in last purchase?
        self.timer1.start(3000)
        self.media_player.player.setMedia(self.media_player.file03)
        self.media_player.player.play()
        self.mylogging.logger.info('websocket_work11 ends')

    def websocket_work11_klas(self, success_order_number):
        """
        My server says that the gesture-pay is successful which indicates the end of such transaction
        :param pay_mode: '1' indicates the order is finished by scanning the QR code; '2' indicates the order is finished by gesture-pay;
        """
        self.mylogging.logger.info('websocket_work11_klas begins')
        # this status will be used after successful elimination of magnetic (work24);
        self.pay_clear_by_gesture = True
        # these two status indicates whether door_controller_work24 is first executed for specific pay-successes transaction.
        self.timer3_not_timeout_status = True
        self.magnetic_signal_not_received = True
        self.success_order_number = success_order_number
        self.door_controller.sendDegauss(1)
        self.door_controller.sendDegauss(1)
        self.timer3.start(500)
        self.mylogging.logger.info('websocket_work11_klas ends')

    def gesture_pay_work12(self):
        """My server says that the gesture-pay is failed since one user only can pay 5 times everyday"""
        self.mylogging.logger.info('gesture_pay_work12 begins')
        self.transaction_not_end_status = False
        self.main_window.toPayFailView(name=self.user_name, image=self.user_portrait)
        self.timer1.start(3000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        self.mylogging.logger.info('gesture_pay_work12 ends')

    def websocket_work12(self):
        """
        My server says that the gesture-pay is failed since the account value is not enough;
        """
        self.mylogging.logger.info('websocket_work12 begins')
        self.transaction_not_end_status = False
        self.main_window.toPayFailView(name=self.user_name, image=self.user_portrait)
        self.timer1.start(3000)
        self.media_player.player.setMedia(self.media_player.file04)
        self.media_player.player.play()
        self.mylogging.logger.info('websocket_work12 ends')

    def websocket_work13(self, door_id):
        """My server says opening the specific door."""
        self.mylogging.logger.info('websocket_work13 begins')
        self.door_controller.sendOpenDoorIn(int(door_id))
        self.media_player.player.setMedia(self.media_player.file01)
        self.media_player.player.play()
        self.mylogging.logger.info('websocket_work13 ends')

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
            # cv2.imwrite(os.path.join(self.working_images_path, '%s_items.jpg' % datetime.strftime('%Y%m%d_%Hh%Mm%Ss')), items_img)
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

    def account_work16_klas(self):
        """
        to show the location of the gesture
        :return:
        """
        self.mylogging.logger.info('account_work16_klas begins')
        # self.mylogging.logger.info('account_work16_klas: x is %s and y is %s' % (self.gesture_frame_location['x'], self.gesture_frame_location['y']))
        self.main_window.showHandGif(x=self.gesture_frame_location['x'],y=self.gesture_frame_location['y'],
                                     length=self.gesture_frame_location['length'],frame=self.thread5.frame)
        self.gesture_frame_frozen_status = True
        self.mylogging.logger.info('account_work16_klas ends')

    def account_work17_klas(self):
        """
        This function is initialized by the failed_detection_local signal which indicates there is no user detected.
        """
        # self.mylogging.logger.info('account_work17_klas begins')

        if self.gesture_frame_frozen_status:
            # adding this since the account thread result might be no well matched user and you freeze the frame.
            self.main_window.stopHandGif()
            self.gesture_frame_frozen_status = False

        # the first way to avoid the restart of the media content;
        # self.failed_detection_local_counter = self.failed_detection_local_counter + 1
        # if self.failed_detection_local_counter > 3:
        #     self.failed_detection_local_counter = 0
        #     self.failed_detection_multiple_counter = 0
        #     self.media_player.player.setMedia(self.media_player.file12)
        #     self.media_player.player.play()

        # the second way to avoid the restart of the media content;
        media_status = self.media_player.player.mediaStatus()
        if media_status == QMediaPlayer.EndOfMedia or media_status == QMediaPlayer.NoMedia:
            self.media_player.player.setMedia(self.media_player.file12)
            self.media_player.player.play()
            self.failed_detection_local_counter = self.failed_detection_local_counter + 1
        if self.failed_detection_local_counter > 9999:
            self.main_window.toPayingView()
            if self.order_link:
                self.main_window.toRegisterView(qrimage=self.make_qrcode(self.order_link))
            else:
                self.main_window.toRegisterView()
            try:
                self.weigher.serial.readyRead.disconnect()
            except BaseException:
                pass
            self.weigher.serial.readyRead.connect(self.weigher.acceptData_back_to_standby)
        else:
            self.thread0_0.start()

        # self.mylogging.logger.info('account_work17_klas ends')

    def account_work18_klas(self):
        """
        This function is initialized by the failed_detection_multiple signal which indicates there are more than one user detected.
        """
        # self.mylogging.logger.info('account_work18_klas begins')
        self.thread0_0.start()
        if self.gesture_frame_frozen_status:
            # adding this since the account thread result might be no well matched user and you freeze the frame.
            self.main_window.stopHandGif()
            self.gesture_frame_frozen_status = False

        # the first way to avoid the restart of the media content;
        # self.failed_detection_multiple_counter = self.failed_detection_multiple_counter + 1
        # if self.failed_detection_multiple_counter > 3:
        #     self.failed_detection_local_counter = 0
        #     self.failed_detection_multiple_counter = 0
        #     self.media_player.player.setMedia(self.media_player.file13)
        #     self.media_player.player.play()

        # the second way to avoid the restart of the media content;
        media_status = self.media_player.player.mediaStatus()
        if media_status == QMediaPlayer.EndOfMedia or media_status == QMediaPlayer.NoMedia:
            self.media_player.player.setMedia(self.media_player.file13)
            self.media_player.player.play()

        # self.mylogging.logger.info('account_work18_klas ends')

    def weigher_work19_klas(self):
        """
        To accelerate the process which is back to the standby layout;
        """
        self.mylogging.logger.info('weigher_work19_klas begins')
        if self.timer1.isActive():
            self.timer1.start(10)  # unit is milli-second
        self.mylogging.logger.info('weigher_work19_klas ends')

    def gesture_pay_work21(self):
        """
        to eliminate the magnetism of items after the successful post of order;
        :return:
        """
        self.mylogging.logger.info('gesture_pay_work21 begins')
        self.door_controller.sendDegauss(1)
        self.mylogging.logger.info('gesture_pay_work21 ends')

    def door_controller_work22(self):
        """
        user has something not payed.
        :param door_id:
        :return:
        """
        self.mylogging.logger.info('door_controller_work22 begins')
        media_status = self.media_player.player.mediaStatus()
        if media_status == QMediaPlayer.EndOfMedia or media_status == QMediaPlayer.NoMedia:
            self.media_player.player.setMedia(self.media_player.file07)
            self.media_player.player.play()
        self.mylogging.logger.info('door_controller_work22 ends')

    def door_controller_work23(self,door_id):
        """
        user finishes the payment or does not buy anything.
        :param door_id:
        :return:
        """
        self.mylogging.logger.info('door_controller_work23 begins')
        self.media_player.player.setMedia(self.media_player.file05)
        self.media_player.player.play()
        # The machine will open the door automatically, hence you do not need to do it manually;
        # self.door_controller.sendOpenDoorOut(int(door_id))
        self.mylogging.logger.info('door_controller_work23 ends')

    def door_controller_work24(self, door_id=1):
        """
        The magnetic of item is eliminated successfully or the self.timer3 timeout;
        :param door_id: this argument has a default value since the QTimer will execute this function and does not provide a value;
        :return:
        """
        self.mylogging.logger.info('door_controller_work24 begins')
        if self.timer3_not_timeout_status and self.magnetic_signal_not_received:
            self.timer3_not_timeout_status = False
            self.magnetic_signal_not_received = False
            self.transaction_not_end_status = False
            self.main_window.toPaySuccessView(name=self.user_name, image=self.user_portrait)

            # I am afraid the network problem and it need to resend them.
            if self.pay_clear_by_gesture:
                self.thread10.img_user = copy.deepcopy(self.user_img)
                self.thread10.img_items = copy.deepcopy(self.items_img)
                self.thread10.img_gesture = copy.deepcopy(self.gesture_img)
                # self.thread11.frame = copy.deepcopy(self.items_img)
            else:
                # if the user pays by QR code, the img_user will be replaced by the gesture_img;
                self.thread10.img_user = copy.deepcopy(self.gesture_img)
                self.thread10.img_items = copy.deepcopy(self.items_img)
                self.thread10.img_gesture = copy.deepcopy(self.gesture_img)
                self.thread11.frame = copy.deepcopy(self.items_img)
            self.thread10.dict01['order_no'] = self.success_order_number
            self.thread10.start()  # What if the image-upload thread still runs since the network problem in last purchase?
            # self.thread11.dict01['order_no'] = self.success_order_number
            # self.thread11.start()
            self.timer1.start(3000)
            self.media_player.player.setMedia(self.media_player.file03)
            self.media_player.player.play()
            self.mylogging.logger.info('door_controller_work24: successes to show the PaySuccessView.')
        self.mylogging.logger.info('door_controller_work24 ends')

    def websocket_work25(self, success_order_number):
        """
        The user finish the payment by QR code;
        :return:
        """
        self.mylogging.logger.info('websocket_work25 begins')
        # this status will be used after successful elimination of magnetic (work24);
        self.pay_clear_by_gesture = False # just used for upload image
        # these two status indicates whether door_controller_work24 is first executed for specific pay-successes transaction.
        self.timer3_not_timeout_status = True
        self.magnetic_signal_not_received = True
        self.success_order_number = success_order_number
        self.door_controller.sendDegauss(1)
        self.door_controller.sendDegauss(1)
        self.timer3.start(500)
        self.mylogging.logger.info('websocket_work25 ends')

    def database_update_work26(self):
        """
        to query the server for database update every 5 minutes.
        :param sku_list:
        :return:
        """
        self.mylogging.logger.info('database_update_work26 starts')
        # self.thread12.start()
        self.database_update_status = True
        self.mylogging.logger.info('database_update_work26 ends')

    def database_update_work27(self, sku_list):
        """
        to tell the server that the local database is updated.
        :param sku_list:
        :return:
        """
        self.mylogging.logger.info('database_update_work27 starts')
        self.mylogging.logger.info(sku_list)
        self.thread13.dict01['sku_ids'] = sku_list
        self.thread13.start()
        self.mylogging.logger.info('database_update_work27 ends')

    def database_update_work28(self, dict_key, image_binary):
        """
        to update the cached dictionary of item imgaes
        :param dict_key: str
        :param image_binary: bytes
        :return:
        """
        self.mylogging.logger.info('database_update_work28 starts')
        new_qpixmap = QPixmap()
        success_status = new_qpixmap.loadFromData(image_binary)
        self.item_images_dict[dict_key] = new_qpixmap
        self.mylogging.logger.info('database_update_work28 ends')

    def account_error01(self):
        """
        The account thread should restart since the network problem(timeout problem);
        """
        self.mylogging.logger.error('account_error01 begins')
        self.error_try_times_account = self.error_try_times_account + 1
        if self.error_try_times_account < 3:
            self.thread5.start()
        else:
            if self.myconfig.data['operating_mode']['normal_error'] == '1':
                self.main_window.showErrorInfo(1)
                self.main_window_error_status = True
            self.mylogging.logger.error('Retry the account thread but errors still exist.')
            self.timer1.start(8*1000)
        self.mylogging.logger.error('account_error01 ends')

    def gesture_pay_error02(self):
        """
        Timeout error happens in the gesture-order thread, the gesture order thread should run again;
        I suggest that ml gesture model should work again to let user do the shopping again;
        """
        # self.thread8.dict01['user_id'] = self.user_id
        # self.thread8.dict01['order_no'] = self.order_number
        # It should use those information it used before; I am afraid that the order is refreshed!
        self.mylogging.logger.error('gesture_pay_error02 begins')
        self.error_try_times_gesture_pay = self.error_try_times_gesture_pay + 1
        if self.error_try_times_gesture_pay < 3:
            self.thread8.start()
        else:
            if self.myconfig.data['operating_mode']['normal_error'] == '1':
                self.main_window.showErrorInfo(1)
                self.main_window_error_status = True
            self.mylogging.logger.error('Retry the gesture pay thread but errors still exist.')
            self.timer1.start(8*1000)
        self.mylogging.logger.error('gesture_pay_error02 ends')

    def image_upload_error03(self):
        """
        Error might happen in the Image_upload thread.
        :return:
        """
        self.mylogging.logger.error('image_upload_error03 begins')
        self.error_try_times_image_upload = self.error_try_times_image_upload + 1
        if self.error_try_times_image_upload < 3:
            self.thread10.start()
        else:
            self.mylogging.logger.error('Retry the image upload thread but errors still exist.')
            # Does not need to reset the timer since it is called in work11;
        self.mylogging.logger.error('image_upload_error03 ends')

    def order_error04(self):
        """
        Error might happen in the QRcode thread.
        In normal situation,
        :return:
        """
        self.mylogging.logger.error('order_error04 begins')
        self.main_window.cleanCommodity()
        self.main_window.setSumPrice('0')
        if self.myconfig.data['operating_mode']['normal_error'] == '1':
            self.main_window.showErrorInfo(1)
            self.main_window_error_status = True
        self.order_number = 'invalid'
        self.new_order_flag = True
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        self.mylogging.logger.error('order_error04 ends')

    def sql_error05(self):
        """
        Error might happen in the SQL thread.
        For instance, the mysql connection is closed since there is no action to query the database over 8 hours.
        """
        self.mylogging.logger.error('sql_error05 begins')
        self.error_try_times_sql = self.error_try_times_sql + 1
        if self.error_try_times_sql < 10:
            self.main_window.cleanCommodity()
            self.main_window.setSumPrice('0')
            self.order_number = 'invalid'
            self.new_order_flag = True
            self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        else:
            if self.myconfig.data['operating_mode']['normal_error'] == '1':
                self.main_window.showErrorInfo(1)
                self.main_window_error_status = True
            self.mylogging.logger.error('Retry the sql thread but errors still exist.')
            self.timer1.start(5*1000)
        self.mylogging.logger.error('sql_error05 ends')

    def sql_error06(self):
        """
        Other error might happen in the SQL thread.
        """
        self.mylogging.logger.error('sql_error06 begins')
        if self.myconfig.data['operating_mode']['normal_error'] == '1':
            self.main_window.showErrorInfo(1)
            self.main_window_error_status = True
        self.main_window.cleanCommodity()
        self.main_window.setSumPrice('0')
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        self.mylogging.logger.error('sql_error06 ends')

    def order_error07(self):
        """
        Error might happen in the order thread;
        For instance, the order number is none;
        """
        self.mylogging.logger.error('order_error07 begins')
        self.order_number = 'invalid'
        self.new_order_flag = True
        if self.myconfig.data['operating_mode']['normal_error'] == '1':
            self.main_window.showErrorInfo(1)
            self.main_window_error_status = True
        self.weigher.serial.readyRead.connect(self.weigher.acceptData_order)
        self.mylogging.logger.error('order_error07 ends')

    def gesture_pay_error08(self):
        """
        The status code of the gesture pay thread is not 200 and the reason is unknown;
        :return:
        """
        self.mylogging.logger.error('gesture_pay_error08 begins')
        self.transaction_not_end_status = False
        self.timer1.start(30 * 1000)
        self.mylogging.logger.error('gesture_pay_error08 ends')

    def make_qrcode(self, content):
        """
        :param content: the url inside the QR code
        :return: PIL.ImageQt.ImageQt class which is like QIamge class!
        """
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=4)
        qr.add_data(content)
        qr.make(fit=True)  # to avoid data overflow errors
        img2 = qr.make_image()
        img2 = img2.convert("RGBA")
        # adding the image to the QR code
        img2_w, img2_h = img2.size
        size_w = int(img2_w / 4)
        size_h = int(img2_h / 4)
        icon_w, icon_h = self.icon_w, self.icon_h
        if self.icon_w > size_w:
            icon_w = size_w
        if self.icon_h > size_h:
            icon_h = size_h
        icon = self.icon.resize((icon_w, icon_h), Image.ANTIALIAS)
        w = int((img2_w - icon_w) / 2)
        h = int((img2_h - icon_h) / 2)
        img2.paste(icon, (w, h), icon)
        return ImageQt(img2)

    def closeEvent(self, event):
        """
        This has unexpected outcome and the reason is not been discovered yet.
        """
        self.mylogging.logger.info('closeEvent (%s): starts to clean memory' %self.__class__)
        if self.myconfig.data['operating_mode']['weight_error'] == '1':
            dialog_status = self.camera_dialog.close()
            self.mylogging.logger.info('The camera item dialog closed with %s' % dialog_status)
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread.
        self.weigher.serial.close()
        self.thread5.status = False
        self.thread8.status = False
        self.thread4.conn.close()
        self.thread0_0.status = False
        self.cam_thread.status = False
        self.user_capture01.release()
        self.capture1.release()
        self.mylogging.logger.info('closeEvent (%s): ends to clean memory' %self.__class__)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        loading_widget = LoadingLayout01()
        loading_widget.show()
        time.sleep(0.5)  # to ensure the paint event is added into the main event loop.
        app.processEvents()
        mainwindow = PaymentSystem_klas()
        mainwindow.main_window.show()
        loading_widget.close()
        sys.exit(app.exec_())
    except BaseException as e:
        print(e)

