"""
Account thread use cv2.CascadeClassifer to detect the face or eyes;
After the detection, the match between the account and the face is finished according the service of Baidu company;
author = hobin;
email = '627227669@qq.com';
"""

import collections
import json
import traceback
from datetime import datetime
import hashlib

import os
import requests
import cv2
import sys
import time
import logging
from PyQt5.QtCore import QThread, pyqtSignal
from memory_profiler import profile


class MyThread4(QThread):
    """
    This is initiated by the sql thread and is used to detect the account of customer;
    """
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread4, self).__init__(parent)
        self.parent = parent
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            print('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                    self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=1)
                    if resp01.status_code == 200:
                        self.dict02 = json.loads(resp01.text)
                        print('Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=1)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                        else:
                            print('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        print('Account thread (end): network problem.')
            elif len(faces) == 0:
                print('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                print('Account thread (end): More than one user in the frame.')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_0_1(QThread):
    """
    Compared with the MyThread4 class, the logging module is added.
    The second difference is that resp01 and resp02 are modified to self.resp01 and self.resp02. This might avoid the memory leaking.
    The third difference is that it emits only the user_info_success signal after the successful detection.
    The fourth difference is that the user name might have some special characters which requires the unicode encoding;
    The fifth difference is that the original header of requests is reloaded by the self.headers01 (the 'Connection' header changes from keep-alive to close);
    """
    user_info_success = pyqtSignal(object, object, object, object)  # user name, user portrait, information about the wechat pay entrust and the the user face
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    failed_detection_multiple = pyqtSignal()
    upload_img = pyqtSignal(object, object)
    timeout_http = pyqtSignal()
    connection_error = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium='app', utm_source='box',
                 face_classifer_path='C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_0_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time': None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_0_1 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_0_1.info('The initialization of the Account thread is successful.')

    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])

        check_str = input + '&' + self.sign_key

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()

        return hexdigest

    def run(self):
        try:
            self.mylogger4_0_1.info('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                    detect_time = datetime.now()
                    self.dict01['client_time'] = str(int(detect_time.timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    self.resp01 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
                    if self.resp01.status_code == 200:
                        self.dict02 = json.loads(self.resp01.text)
                        # print('Account thread: %s' % self.dict02)
                        self.mylogger4_0_1.info(u'Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            self.resp02 = requests.get(self.dict02['data']['avatar_url'], headers=self.headers01, timeout=8)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            self.mylogger4_0_1.info(
                                u'Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.upload_img.emit(self.frame, detect_time)
                            self.user_info_success.emit(self.dict02['data']['nick_name'], self.resp02.content,
                                                        self.dict02['data']['wxpay_entrust'],
                                                        self.frame[y:y + h, x:x + w, :])
                        else:
                            self.mylogger4_0_1.info('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        # the network problem might be 404?
                        self.mylogger4_0_1.info('Account thread (end): network problem.')
            elif len(faces) == 0:
                self.mylogger4_0_1.info('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                self.mylogger4_0_1.info('Account thread (end): More than one user in the frame.')
                self.failed_detection_multiple.emit()
        except requests.exceptions.ReadTimeout:
            self.mylogger4_0_1.error(
                '***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except requests.exceptions.ConnectionError:
            self.mylogger4_0_1.error('***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.connection_error.emit()
        except BaseException as e:
            self.mylogger4_0_1.error(
                '***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.error.emit()


class MyThread4_0_1_1(QThread):
    """
    Compared with MyThread4_0_1 class, this class will emits the 'freezing_gesture' signal after detecting only one face;
    """
    user_info_success = pyqtSignal(object, object, object, object)  # user name, user portrait, information about the wechat pay entrust and the the user face
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    failed_detection_multiple = pyqtSignal()
    upload_img = pyqtSignal(object, object)
    timeout_http = pyqtSignal()
    connection_error = pyqtSignal()
    error = pyqtSignal()
    freezing_gesture = pyqtSignal()

    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium='app', utm_source='box',
                 face_classifer_path='C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_0_1_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time': None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_0_1_1 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_0_1_1.info('The initialization of the Account thread is successful.')

    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])

        check_str = input + '&' + self.sign_key

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()

        return hexdigest

    def run(self):
        try:
            self.mylogger4_0_1_1.info('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                self.freezing_gesture.emit()  # The type of the 'freezing_gesture' signal connection should be Qt.BlockingQueuedConnection
                self.mylogger4_0_1_1.info('Account thread: freezing success.')
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                    detect_time = datetime.now()
                    self.dict01['client_time'] = str(int(detect_time.timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    self.resp01 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
                    if self.resp01.status_code == 200:
                        self.dict02 = json.loads(self.resp01.text)
                        # print('Account thread: %s' % self.dict02)
                        self.mylogger4_0_1_1.info(u'Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            self.resp02 = requests.get(self.dict02['data']['avatar_url'], headers=self.headers01, timeout=8)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            self.mylogger4_0_1_1.info(
                                u'Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.upload_img.emit(self.frame, detect_time)
                            self.user_info_success.emit(self.dict02['data']['nick_name'], self.resp02.content,
                                                        self.dict02['data']['wxpay_entrust'],
                                                        self.frame[y:y + h, x:x + w, :])
                        else:
                            self.mylogger4_0_1_1.info('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        # the network problem might be 404?
                        self.mylogger4_0_1_1.info('Account thread (end): network problem.')
            elif len(faces) == 0:
                self.mylogger4_0_1_1.info('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                self.mylogger4_0_1_1.info('Account thread (end): More than one user in the frame.')
                self.failed_detection_multiple.emit()
        except requests.exceptions.ReadTimeout:
            self.mylogger4_0_1_1.error(
                '***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except requests.exceptions.ConnectionError:
            self.mylogger4_0_1_1.error('***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.connection_error.emit()
        except BaseException as e:
            self.mylogger4_0_1_1.error(
                '***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.error.emit()


class MyThread4_0_1_2(QThread):
    """
    Compared with MyThread4_0_1 class, this class will emits the 'freezing_gesture' signal after detecting only one face;
    Compared with MyThread4_0_1_1 class, this class will emit the user head rather than the user face image by using finding_head_from_face;
    """
    user_info_success = pyqtSignal(object, object, object, object)  # user name, user portrait, information about the wechat pay entrust and the the user head
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    failed_detection_multiple = pyqtSignal()
    upload_img = pyqtSignal(object, object)
    timeout_http = pyqtSignal()
    connection_error = pyqtSignal()
    error = pyqtSignal()
    freezing_gesture = pyqtSignal()

    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium='app', utm_source='box',
                 face_classifer_path='C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_0_1_2, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time': None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_0_1_2 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_0_1_2.info('The initialization of the Account thread is successful.')

    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])

        check_str = input + '&' + self.sign_key

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()

        return hexdigest

    def finding_head_from_face(self, x, y, w, h, frame_width, frame_height,
                               increment_factor_left=0.25, increment_factor_top=0.25,
                               increment_factor_right=0.25, increment_factor_bottom=0.25):
        """
        :param x:
        :param y:
        :param w: this value is provided by the
        :param h:
        :param frame_width:
        :param frame_height:
        :param increment_factor_left: this factor is related to the parameter w
        :param increment_factor_top: this factor is related to the parameter h
        :param increment_factor_right: this factor is related to the parameter w
        :param increment_factor_bottom: this factor is related to the parameter h
        :return: a tuple and the data format is like (x, y, x_end, y_end)
        """
        x_start_init = int(x - w * increment_factor_left)
        y_start_init = int(y - h * increment_factor_top)
        x_start = x_start_init if x_start_init > 0 else 0
        y_start = y_start_init if y_start_init > 0 else 0
        x_end_init = int(x_start + w * (1 + increment_factor_left + increment_factor_right))
        y_end_init = int(y_start + h * (1 + increment_factor_top + increment_factor_bottom))
        x_end = x_end_init if x_end_init < frame_width else frame_width - 1  # 'minus 1' to ensure the end is not out of the range of index
        y_end = y_end_init if y_end_init < frame_height else frame_height - 1  # 'minus 1' to ensure the end is not out of the range of index
        return (x_start, y_start, x_end, y_end)

    def run(self):
        try:
            self.mylogger4_0_1_2.info('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                self.freezing_gesture.emit()  # The type of the 'freezing_gesture' signal connection should be Qt.BlockingQueuedConnection
                self.mylogger4_0_1_2.info('Account thread: freezing success.')
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                    detect_time = datetime.now()
                    self.dict01['client_time'] = str(int(detect_time.timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    self.resp01 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
                    if self.resp01.status_code == 200:
                        self.dict02 = json.loads(self.resp01.text)
                        # print('Account thread: %s' % self.dict02)
                        self.mylogger4_0_1_2.info(u'Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            self.resp02 = requests.get(self.dict02['data']['avatar_url'], headers=self.headers01, timeout=8)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            self.mylogger4_0_1_2.info(
                                u'Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.upload_img.emit(self.frame, detect_time)
                            # Be careful about the frame shape of openCV: height, width, depth;
                            head_x_start, head_y_start, head_x_end, head_y_end = self.finding_head_from_face(
                                x,y,w,h,frame_width=self.frame.shape[1],frame_height=self.frame.shape[0])
                            self.user_info_success.emit(self.dict02['data']['nick_name'], self.resp02.content,
                                                        self.dict02['data']['wxpay_entrust'],
                                                        self.frame[head_y_start:head_y_end, head_x_start:head_x_end, :])
                        else:
                            self.mylogger4_0_1_2.info('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        # the network problem might be 404?
                        self.mylogger4_0_1_2.info('Account thread (end): network problem.')
            elif len(faces) == 0:
                self.mylogger4_0_1_2.info('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                self.mylogger4_0_1_2.info('Account thread (end): More than one user in the frame.')
                self.failed_detection_multiple.emit()
        except requests.exceptions.ReadTimeout:
            self.mylogger4_0_1_2.error(
                '***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except requests.exceptions.ConnectionError:
            self.mylogger4_0_1_2.error('***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.connection_error.emit()
        except BaseException as e:
            self.mylogger4_0_1_2.error(
                '***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.error.emit()


class MyThread4_0_1_3(QThread):
    """
    Compared with MyThread4_0_1 class, this class will emits the 'freezing_gesture' signal after detecting only one face;
    Compared with MyThread4_0_1_1 class, this class will emit the user head rather than the user face image by using finding_head_from_face;
    Compared with MyThread4_0_1_2 class, this class will try to get the user wechat image and if this fails, it will use default image instead;
    Compared with MyThread4_0_1_2 class, this class will emit the user head when there is no well-matched user.
    """
    user_info_success = pyqtSignal(object, object, object, object)  # user name, user portrait, information about the wechat pay entrust and the the user head
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_web_klas = pyqtSignal(object) # the user head,
    failed_detection_local = pyqtSignal()
    failed_detection_multiple = pyqtSignal()
    upload_img = pyqtSignal(object, object)
    timeout_http = pyqtSignal()
    connection_error = pyqtSignal()
    error = pyqtSignal()
    freezing_gesture = pyqtSignal()

    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium='app', utm_source='box',
                 face_classifer_path='C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_0_1_3, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time': None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        dir_path = os.path.dirname(__file__)
        image_path = os.path.join(dir_path, 'Images','DefaultPortrait.jpg')
        with open(image_path,'rb') as img_binary:
            self.default_user_portrait = img_binary.read()
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_0_1_3 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_0_1_3.info('The initialization of the Account thread is successful.')

    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])

        check_str = input + '&' + self.sign_key

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()

        return hexdigest

    def finding_head_from_face(self, x, y, w, h, frame_width, frame_height,
                               increment_factor_left=0.25, increment_factor_top=0.25,
                               increment_factor_right=0.25, increment_factor_bottom=0.25):
        """
        :param x:
        :param y:
        :param w: this value is provided by the
        :param h:
        :param frame_width:
        :param frame_height:
        :param increment_factor_left: this factor is related to the parameter w
        :param increment_factor_top: this factor is related to the parameter h
        :param increment_factor_right: this factor is related to the parameter w
        :param increment_factor_bottom: this factor is related to the parameter h
        :return: a tuple and the data format is like (x, y, x_end, y_end)
        """
        x_start_init = int(x - w * increment_factor_left)
        y_start_init = int(y - h * increment_factor_top)
        x_start = x_start_init if x_start_init > 0 else 0
        y_start = y_start_init if y_start_init > 0 else 0
        x_end_init = int(x_start + w * (1 + increment_factor_left + increment_factor_right))
        y_end_init = int(y_start + h * (1 + increment_factor_top + increment_factor_bottom))
        x_end = x_end_init if x_end_init < frame_width else frame_width - 1  # 'minus 1' to ensure the end is not out of the range of index
        y_end = y_end_init if y_end_init < frame_height else frame_height - 1  # 'minus 1' to ensure the end is not out of the range of index
        return (x_start, y_start, x_end, y_end)

    def run(self):
        try:
            self.mylogger4_0_1_3.info('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(100, 100))
            if len(faces) == 1:
                self.freezing_gesture.emit()  # The type of the 'freezing_gesture' signal connection should be Qt.BlockingQueuedConnection
                self.mylogger4_0_1_3.info('Account thread: freezing success.')
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                    detect_time = datetime.now()
                    self.dict01['client_time'] = str(int(detect_time.timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    self.mylogger4_0_1_3.info('Account thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
                    self.resp01 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
                    if self.resp01.status_code == 200:
                        self.dict02 = json.loads(self.resp01.text)
                        # print('Account thread: %s' % self.dict02)
                        self.mylogger4_0_1_3.info(u'Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            try:
                                self.resp02 = requests.get(self.dict02['data']['avatar_url'], headers=self.headers01,timeout=8)
                                self.mylogger4_0_1_3.info(
                                    u'Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.upload_img.emit(self.frame, detect_time)
                                # Be careful about the frame shape of openCV: height, width, depth;
                                head_x_start, head_y_start, head_x_end, head_y_end = self.finding_head_from_face(
                                    x, y, w, h, frame_width=self.frame.shape[1], frame_height=self.frame.shape[0])
                                self.user_info_success.emit(self.dict02['data']['nick_name'], self.resp02.content,
                                                            self.dict02['data']['wxpay_entrust'],
                                                            self.frame[head_y_start:head_y_end, head_x_start:head_x_end,
                                                            :])
                            except BaseException:
                                # using default user image
                                self.mylogger4_0_1_3.info(
                                    u'Account thread (end): the user is %s and using default user portrait.' % self.dict02['data']['nick_name'])
                                self.upload_img.emit(self.frame, detect_time)
                                # Be careful about the frame shape of openCV: height, width, depth;
                                head_x_start, head_y_start, head_x_end, head_y_end = self.finding_head_from_face(
                                    x, y, w, h, frame_width=self.frame.shape[1], frame_height=self.frame.shape[0])
                                self.user_info_success.emit(self.dict02['data']['nick_name'], self.default_user_portrait,
                                                            self.dict02['data']['wxpay_entrust'],
                                                            self.frame[head_y_start:head_y_end, head_x_start:head_x_end,:])
                        else:
                            self.mylogger4_0_1_3.info('Account thread (end): No well-matched user.')
                            head_x_start, head_y_start, head_x_end, head_y_end = self.finding_head_from_face(
                                x, y, w, h, frame_width=self.frame.shape[1], frame_height=self.frame.shape[0])
                            self.failed_detection_web_klas.emit(self.frame[head_y_start:head_y_end, head_x_start:head_x_end,:])
                    else:
                        # the network problem might be 404?
                        self.mylogger4_0_1_3.info('Account thread (end): network problem.')
            elif len(faces) == 0:
                self.mylogger4_0_1_3.info('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                self.mylogger4_0_1_3.info('Account thread (end): More than one user in the frame.')
                self.failed_detection_multiple.emit()
        except requests.exceptions.ReadTimeout:
            self.mylogger4_0_1_3.error(
                '***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except requests.exceptions.ConnectionError:
            self.mylogger4_0_1_3.error('***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.connection_error.emit()
        except BaseException as e:
            self.mylogger4_0_1_3.error(
                '***------------------------Be careful! Error occurs in account thread!------------------------***', exc_info=True)
            self.error.emit()


class MyThread4_0_2(QThread):
    """
    This is initiated by the sql thread and is used to detect the account of customer;
    Compared with the MyThread4 class, this class will fix the detected faces if the detected faces is outside the original image;
    """
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread4_0_2, self).__init__(parent)
        self.parent = parent
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def fixing_face_rectangle(self, x, y, w, h, frame_width, frame_height):
        """
        fixing the detected face if it is outside the original frame;
        :param x:
        :param y:
        :param w:
        :param h:
        :return: (x, y, w, h)
        """
        x_start = x if x > 0 else 0
        y_start = y if y > 0 else 0
        x_end = x + w if x + w < frame_width else frame_width -1  # 'minus 1' to ensure the end is not out of the range of index
        y_end = y + h if y + h < frame_height else frame_height -1 # 'minus 1' to ensure the end is not out of the range of index
        return (x_start, y_start, x_end-x_start, y_end-y_start)


    def run(self):
        try:
            print('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    (x, y, w, h) = self.fixing_face_rectangle(x, y, w, h, self.frame.shape[0], self.frame.shape[1])
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                    self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=1)
                    if resp01.status_code == 200:
                        self.dict02 = json.loads(resp01.text)
                        print('Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=1)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                        else:
                            print('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        print('Account thread (end): network problem.')
            elif len(faces) == 0:
                print('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                print('Account thread (end): More than one user in the frame.')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_0_3(QThread):
    """
    This is initiated by the sql thread and is used to detect the account of customer;
    Compared with the MyThread4 class, it use request.session to do the http request;
    """
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread4_0_3, self).__init__(parent)
        self.parent = parent
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            print('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                    self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    # resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=1)
                    with requests.session() as sess01:
                        # sess01.keep_alive = False
                        sess01.headers['Connection'] = 'close'
                        print('Account thread: the header in the first session is: %s' %sess01.headers)
                        resp01 = sess01.post(self.url, files=self.files, data=self.dict01, timeout=5)
                    if resp01.status_code == 200:
                        self.dict02 = json.loads(resp01.text)
                        print('Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            # resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=1)
                            with requests.session() as sess02:
                                # sess02.keep_alive = False
                                sess02.headers['Connection'] = 'close'
                                print('Account thread: the header in the second session is: %s' % sess02.headers)
                                resp02 = sess02.get(self.dict02['data']['avatar_url'], timeout=5)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                        else:
                            print('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        print('Account thread (end): network problem.')
            elif len(faces) == 0:
                print('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                print('Account thread (end): More than one user in the frame.')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_T1(MyThread4):
    """
    This is initiated by the sql thread and is used to detect the account of customer;
    It is monitored by memory_profile to check the memory leak.
    """
    def __init__(self, parent=None):
        super(MyThread4_T1, self).__init__(parent)

    @profile(precision=2)
    def run(self):
        try:
            print('Account thread begins')
            img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
            # It returns the positions of detected faces
            # Currently, the size of the detected faces should be larger the size(565, 424)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
            if len(faces) == 1:
                for (x, y, w, h) in faces:
                    # the rectangle (detected face) may be partially outside the original image;
                    rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                    self.files['face_photo'] = buffer.tostring()
                    # print(len(image_encoded.tostring()))
                    # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                    self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                    self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                    # print(self.dict01)
                    resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=1)
                    if resp01.status_code == 200:
                        self.dict02 = json.loads(resp01.text)
                        print('Account thread: %s' % self.dict02)
                        if self.dict02['code'] == 200:
                            resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=1)
                            # print(resp02.headers['content-type'])
                            # print(type(resp02.content))  # the binary data representing the jpg image
                            print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                            self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                        else:
                            print('Account thread (end): No well-matched user.')
                            self.failed_detection_web.emit()
                    else:
                        print('Account thread (end): network problem.')
            elif len(faces) == 0:
                print('Account thread (end): No user in the frame.')
                self.failed_detection_local.emit()
            elif len(faces) >= 2:
                print('Account thread (end): More than one user in the frame.')
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_1(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    """
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent=None):
        super(MyThread4_1, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            self.status = True
            while self.status:
                print('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                        self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=3)
                        if resp01.status_code == 200:
                            self.dict02 = json.loads(resp01.text)
                            print('Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=3)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                                self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                                self.status = False
                            else:
                                print('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            print('Account thread (end): network problem.')
                elif len(faces) == 0:
                    print('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    print('Account thread (end): More than one user in the frame.')
                time.sleep(1)
        except requests.exceptions.ReadTimeout:
            print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_2(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    """
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent=None):
        super(MyThread4_2, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            self.status = True
            while self.status:
                print('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                _, self.frame = self.parent.user_interface.camera.read()
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                        self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=3)
                        if resp01.status_code == 200:
                            self.dict02 = json.loads(resp01.text)
                            print('Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=3)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                                self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                                self.status = False
                            else:
                                print('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            print('Account thread (end): network problem.')
                elif len(faces) == 0:
                    print('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    print('Account thread (end): More than one user in the frame.')
                time.sleep(1)
        except requests.exceptions.ReadTimeout:
            print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_3(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    The fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    """
    success = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent):
        super(MyThread4_3, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            self.status = True
            while self.status:
                print('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;
                        self.dict01['client_time'] = str(int(datetime.now().timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=3)
                        if resp01.status_code == 200:
                            self.dict02 = json.loads(resp01.text)
                            print('Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=3)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.status = False
                                self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                                self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                            else:
                                print('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            print('Account thread (end): network problem.')
                elif len(faces) == 0:
                    print('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    print('Account thread (end): More than one user in the frame.')

                time.sleep(1)
                if  self.parent.timer1.isActive():
                    pass
                else:
                    self.status = False  # close itself since the payment system is in stand-by status;
        except requests.exceptions.ReadTimeout:
            print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_4(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Compared with the MyThread4_3 class, the difference is saving the image;
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    The fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    """
    success = pyqtSignal(object, object)
    upload_img = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent):
        super(MyThread4_4, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.url = 'http://api.commaai.cn//v1/face/find_user'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':'app',
                       'utm_source':'box',
                       'store_id': '2',
                       'client_time':None}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            self.status = True
            while self.status:
                print('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                        detect_time = datetime.now()
                        self.dict01['client_time'] = str(int(detect_time.timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=3)
                        if resp01.status_code == 200:
                            self.dict02 = json.loads(resp01.text)
                            print('Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=3)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.status = False
                                self.upload_img.emit(self.frame, detect_time)
                                self.success.emit(self.dict02['data']['nick_name'], resp02.content)
                                self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                            else:
                                print('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            print('Account thread (end): network problem.')
                elif len(faces) == 0:
                    print('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    print('Account thread (end): More than one user in the frame.')

                time.sleep(1)
                if  self.parent.timer1.isActive():
                    pass
                else:
                    self.status = False  # close itself since the payment system is in stand-by status;
        except requests.exceptions.ReadTimeout:
            print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_4_1(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Compared with the MyThread4_3 class, the difference is saving the image;
    Compared with the MyThread4_3 class, another difference is that the refresh of the image should be inside the while loop;
    Compared with the MyThread4_3 class, the third difference is that the thread stops itself since the while loop;
    Compared with the MyThread4_3 class, the fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    Compared with the MyThread4_4 class, the logging module is introduced to this module at first time.
    Compared with the MyThread4_4 class, resp01 and resp02 are modified to self.resp01 and self.resp02.
    """
    success = pyqtSignal(object, object)
    upload_img = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium = 'app',utm_source = 'box',
                 face_classifer_path = 'C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_4_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time':None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_4_1 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_4_1.info('The initialization of the Account thread is successful.')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            self.status = True
            while self.status:
                # print('Account thread begins')
                self.mylogger4_4_1.info('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                        detect_time = datetime.now()
                        self.dict01['client_time'] = str(int(detect_time.timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        self.resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=8)
                        if self.resp01.status_code == 200:
                            self.dict02 = json.loads(self.resp01.text)
                            # print('Account thread: %s' % self.dict02)
                            self.mylogger4_4_1.info('Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                self.resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=8)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                # print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.mylogger4_4_1.info('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.status = False
                                self.upload_img.emit(self.frame, detect_time)
                                self.success.emit(self.dict02['data']['nick_name'], self.resp02.content)
                                self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                            else:
                                # print('Account thread (end): No well-matched user.')
                                self.mylogger4_4_1.info('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            # print('Account thread (end): network problem.')
                            self.mylogger4_4_1.info('Account thread (end): network problem.')
                elif len(faces) == 0:
                    # print('Account thread (end): No user in the frame.')
                    self.mylogger4_4_1.info('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    # print('Account thread (end): More than one user in the frame.')
                    self.mylogger4_4_1.info('Account thread (end): More than one user in the frame.')

                if  self.parent.timer1.isActive():
                    if self.status:
                        time.sleep(1)
                else:
                    self.status = False  # close itself since the payment system is in stand-by status;
        except requests.exceptions.ReadTimeout:
            # print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.mylogger4_4_1.error('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            # print(''.join(traceback.format_exception(*sys.exc_info())))
            # print('***------------------------Be careful! Error occurs in account thread!------------------------***')
            self.mylogger4_4_1.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.mylogger4_4_1.error('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_4_2(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Compared with the MyThread4_3 class, the difference is saving the image;
    Compared with the MyThread4_3 class, another difference is that the refresh of the image should be inside the while loop;
    Compared with the MyThread4_3 class, the third difference is that the thread stops itself since the while loop;
    Compared with the MyThread4_3 class, the fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    Compared with the MyThread4_4 class, the logging module is introduced to this module at first time.
    Compared with the MyThread4_4 class, resp01 and resp02 are modified to self.resp01 and self.resp02.
    Compared with the MyThread4_4_1 class, this class emits only the user_info_success signal after the successful detection.
    The user_info_success signal will carry the user name, user portrait, information about the wechat pay entrust and the the user face.
    The refresh of the camera frame is extracted to a new function camera_frame_refresh;
    The user name might have some special characters which requires the unicode encoding;
    """
    user_info_success = pyqtSignal(object, object, object, object)  # user name, user portrait, information about the wechat pay entrust and the the user face
    success = pyqtSignal(object, object)
    upload_img = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium = 'app',utm_source = 'box',
                 face_classifer_path = 'C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_4_2, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time':None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_4_2 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_4_2.info('The initialization of the Account thread is successful.')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def camera_frame_refresh(self):
        return self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame


    def run(self):
        try:
            self.status = True
            while self.status:
                # print('Account thread begins')
                self.mylogger4_4_2.info('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                self.frame = self.camera_frame_refresh()
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                        detect_time = datetime.now()
                        self.dict01['client_time'] = str(int(detect_time.timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        self.resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=8)
                        if self.resp01.status_code == 200:
                            self.dict02 = json.loads(self.resp01.text)
                            # print('Account thread: %s' % self.dict02)
                            self.mylogger4_4_2.info(u'Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                self.resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=8)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                # print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.mylogger4_4_2.info(u'Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.status = False
                                self.upload_img.emit(self.frame, detect_time)
                                # self.success.emit(self.dict02['data']['nick_name'], self.resp02.content)
                                # self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                                self.user_info_success.emit(self.dict02['data']['nick_name'], self.resp02.content, self.dict02['data']['wxpay_entrust'], self.frame[y:y + h, x:x + w, :])
                            else:
                                # print('Account thread (end): No well-matched user.')
                                self.mylogger4_4_2.info('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            # print('Account thread (end): network problem.')
                            self.mylogger4_4_2.info('Account thread (end): network problem.')
                elif len(faces) == 0:
                    # print('Account thread (end): No user in the frame.')
                    self.mylogger4_4_2.info('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    # print('Account thread (end): More than one user in the frame.')
                    self.mylogger4_4_2.info('Account thread (end): More than one user in the frame.')

                if  self.parent.timer1.isActive():
                    if self.status:
                        time.sleep(1)
                else:
                    self.status = False  # close itself since the payment system is in stand-by status;
        except requests.exceptions.ReadTimeout:
            # print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.mylogger4_4_2.error('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            # print(''.join(traceback.format_exception(*sys.exc_info())))
            # print('***------------------------Be careful! Error occurs in account thread!------------------------***')
            self.mylogger4_4_2.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.mylogger4_4_2.error('***------------------------Be careful! Error occurs in account thread!------------------------***')


class MyThread4_4_2_klas(MyThread4_4_2):
    def __init__(self, parent, **kwargs):
        super(MyThread4_4_2_klas, self).__init__(parent=parent, **kwargs)

    def camera_frame_refresh(self):
        ret, frame = self.parent.main_window.getCamera().read()
        return frame


class MyThread4_4_3(QThread):
    """
    Compared with the MyThread4 class, one main difference is the while loop in its run();
    Compared with the MyThread4_3 class, the difference is saving the image;
    Compared with the MyThread4_3 class, another difference is that the refresh of the image should be inside the while loop;
    Compared with the MyThread4_3 class, the third difference is that the thread stops itself since the while loop;
    Compared with the MyThread4_3 class, the fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    Compared with the MyThread4_4 class, the logging module is introduced to this module at first time.
    Compared with the MyThread4_4 class, resp01 and resp02 are modified to self.resp01 and self.resp02.
    Compared with the MyThread4_4_1 class, this class emits only the user_info2_success signal after the successful detection.
    The user_info2_success signal will carry the user name, information about the wechat pay entrust and the the user face.
    Compared with the MyThread4_4_2 class, this class does not need the user portrait and hence the second request is removed.
    """
    user_info_success = pyqtSignal(object, object, object, object)
    user_info2_success = pyqtSignal(object, object, object)
    success = pyqtSignal(object, object)
    upload_img = pyqtSignal(object, object)
    failed_detection_web = pyqtSignal()
    failed_detection_local = pyqtSignal()
    timeout_http = pyqtSignal()
    wechatpay_entrust = pyqtSignal(object)


    def __init__(self, parent, logger_name='hobin', *, url='http://api.commaai.cn//v1/face/find_user',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', store_id='2',
                 utm_medium = 'app',utm_source = 'box',
                 face_classifer_path = 'C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 **kwargs):
        super(MyThread4_4_3, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.files = {'face_photo': None}
        self.dict01 = {"api_sign":None,
                       'utm_medium':utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'client_time':None}
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.files = {'face_photo': None}
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'client_time': None}
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])

        # some variables
        self.parent = parent
        self.status = True
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.resp01 = None
        self.resp02 = None
        self.mylogger4_4_3 = logging.getLogger(logger_name)
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger4_4_3.info('The initialization of the Account thread is successful.')


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return:
        """
        ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

        input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

        check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            self.status = True
            while self.status:
                # print('Account thread begins')
                self.mylogger4_4_3.info('Account thread begins')
                # the current parent is required to be the QMainWindow class (the top most widget);
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)  # the oepnCV example requires this;
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                # cv2.imwrite('D:\\hobin%s.png' % str(int(datetime.now().timestamp())), gray)
                # It returns the positions of detected faces
                # Currently, the size of the detected faces should be larger the size(565, 424)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))
                if len(faces) == 1:
                    for (x, y, w, h) in faces:
                        # the rectangle (detected face) may be partially outside the original image;
                        rect, buffer = cv2.imencode('.jpg', self.frame[y:y + h, x:x + w, :])
                        self.files['face_photo'] = buffer.tostring()
                        # print(len(image_encoded.tostring()))
                        # print(len(bytes(image_encoded)))  # the second way to get the right format for posting it to server;

                        detect_time = datetime.now()
                        self.dict01['client_time'] = str(int(detect_time.timestamp()))
                        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
                        # print(self.dict01)
                        self.resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=8)
                        if self.resp01.status_code == 200:
                            self.dict02 = json.loads(self.resp01.text)
                            # print('Account thread: %s' % self.dict02)
                            self.mylogger4_4_3.info('Account thread: %s' % self.dict02)
                            if self.dict02['code'] == 200:
                                # self.resp02 = requests.get(self.dict02['data']['avatar_url'], timeout=8)
                                # print(resp02.headers['content-type'])
                                # print(type(resp02.content))  # the binary data representing the jpg image
                                # print('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.mylogger4_4_3.info('Account thread (end): the user is %s' % self.dict02['data']['nick_name'])
                                self.status = False
                                self.upload_img.emit(self.frame, detect_time)
                                # self.success.emit(self.dict02['data']['nick_name'], self.resp02.content)
                                # self.wechatpay_entrust.emit(self.dict02['data']['wxpay_entrust'])
                                # self.user_info_success.emit(self.dict02['data']['nick_name'], self.resp02.content, self.dict02['data']['wxpay_entrust'], self.frame[y:y + h, x:x + w, :])
                                self.user_info2_success.emit(self.dict02['data']['nick_name'], self.dict02['data']['wxpay_entrust'], self.frame[y:y + h, x:x + w, :])
                            else:
                                # print('Account thread (end): No well-matched user.')
                                self.mylogger4_4_3.info('Account thread (end): No well-matched user.')
                                self.failed_detection_web.emit()
                        else:
                            # print('Account thread (end): network problem.')
                            self.mylogger4_4_3.info('Account thread (end): network problem.')
                elif len(faces) == 0:
                    # print('Account thread (end): No user in the frame.')
                    self.mylogger4_4_3.info('Account thread (end): No user in the frame.')
                    self.failed_detection_local.emit()
                elif len(faces) >= 2:
                    # print('Account thread (end): More than one user in the frame.')
                    self.mylogger4_4_3.info('Account thread (end): More than one user in the frame.')

                if  self.parent.timer1.isActive():
                    if self.status:
                        time.sleep(1)
                else:
                    self.status = False  # close itself since the payment system is in stand-by status;
        except requests.exceptions.ReadTimeout:
            # print('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.mylogger4_4_3.error('***------------------------Network problem happens (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except BaseException:
            # print(''.join(traceback.format_exception(*sys.exc_info())))
            # print('***------------------------Be careful! Error occurs in account thread!------------------------***')
            self.mylogger4_4_3.error(''.join(traceback.format_exception(*sys.exc_info())))
            self.mylogger4_4_3.error('***------------------------Be careful! Error occurs in account thread!------------------------***')


if __name__ == '__main__':
    a = MyThread4_0_3()
    a.frame = cv2.imread('D:\\01PythonFile\\basicTest\\images\\linchao.jpg')
    # print(type(a.frame))  # ndarray type
    # print(a.frame.shape)  # (1440, 1080, 3)

    # for only one time
    a.start()
    while a.isRunning():
        pass

    # for memory leak
    # counter = 50
    # while counter >0:
    #     a.start()
    #     while a.isRunning():
    #         pass
    #     counter = counter - 1


