"""
Account thread use cv2.CascadeClassifer to detect the face or eyes;
After the detection, the match between the account and the face is finished according the service of Baidu company;
author = hobin
"""

import collections
import json
import traceback
from datetime import datetime
import hashlib
import requests
import cv2
import sys
import time
import logging
from PyQt5.QtCore import QThread, pyqtSignal


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


if __name__ == '__main__':
    a = MyThread4()
    a.frame = cv2.imread('D:\\01PythonFile\\basicTest\\images\\linchao.jpg')
    # print(type(a.frame))  # ndarray type
    # print(a.frame.shape)  # (1440, 1080, 3)
    a.start()
    while a.isRunning():
        pass

