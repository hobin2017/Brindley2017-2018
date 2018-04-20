# -*- coding: utf-8 -*-
"""

"""
import collections
import hashlib
import json
from datetime import datetime
import logging
import cv2
import requests
from PyQt5.QtCore import QThread, pyqtSignal


class MyThread9(QThread):
    """
    It is used to upload images after the payment is finished.
    The server only accepts one image at one time.
    """
    error = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread9, self).__init__(parent)
        self.parent = parent
        self.url = 'http://api.commaai.cn/order/attach/upload_payment_attach'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.img_user = None
        self.img_gesture = None
        self.img_items = None
        self.files = {'picture': None}
        # if attach_type =1, it indicates the image is related to the user.
        # if attach_type =2, it indicates the image is related to gesture-pay.
        # if attach_type =3, it indicates the image is about items.
        self.dict01 = {"api_sign": None,
                       'utm_medium': 'app',
                       'utm_source': 'box',
                       'order_no': '',
                       'attach_type': '',
                       'client_time': None}
        self.dict02 = {}  # the dictionary object of the first HTTP result.


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
        print('Image-upload thread begins')
        # the value of self.dict01['order_no'] is given before the run function and it is 'str' type;
        # the value of self.image is given before the run function and it is 'str' type;
        try:
            # prepare to upload the first image
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['attach_type'] = '1'
            ret, buffer = cv2.imencode('.jpg', self.img_user)
            self.files['picture'] = buffer.tostring()
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp01 = requests.post(self.url, files=self.files, data=self.dict01, timeout=5)
            if resp01.status_code == 200:
                self.dict02 = json.loads(resp01.text)
                print(self.dict02)
                print('Image-upload thread with type %s ends.' % self.dict01['attach_type'])
            else:
                print('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])  # E.g. 404
            # prepare to upload the second image
            self.dict01['attach_type'] = '2'
            ret, buffer = cv2.imencode('.jpg', self.img_gesture)
            self.files['picture'] = buffer.tostring()
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp02 = requests.post(self.url, files=self.files, data=self.dict01, timeout=5)
            if resp02.status_code == 200:
                self.dict02 = json.loads(resp02.text)
                print(self.dict02)
                print('Image-upload thread with type %s ends.' % self.dict01['attach_type'])
            else:
                print(
                    'Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])  # E.g. 404
            # prepare to upload the third image
            self.dict01['attach_type'] = '3'
            ret, buffer = cv2.imencode('.jpg', self.img_items)
            self.files['picture'] = buffer.tostring()
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp03 = requests.post(self.url, files=self.files, data=self.dict01, timeout=5)
            if resp03.status_code == 200:
                self.dict02 = json.loads(resp03.text)
                print(self.dict02)
                print('Image-upload thread with type %s ends.' % self.dict01['attach_type'])
            else:
                print(
                    'Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])  # E.g. 404
        except BaseException as e:
            print(e)
            print('-------------------------Error happens in Image-upload thread.----------------------------')
            self.error.emit()


class MyThread9_1(QThread):
    """
    It is used to upload images after the payment is finished.
    The server only accepts one image at one time.
    Compared with the MyThread9 class, the logging module is introduced to this module at first time.
    Compared with the MyThread9 class, the original header of requests is reloaded by the self.headers01 (the 'Connection' header changes from keep-alive to close);
    """
    error = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, url = 'http://api.commaai.cn/order/attach/upload_payment_attach',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', utm_medium = 'app', utm_source = 'box', **kwargs):
        super(MyThread9_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        # if attach_type =1, it indicates the image is related to the user.
        # if attach_type =2, it indicates the image is related to gesture-pay.
        # if attach_type =3, it indicates the image is about items.
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'order_no': '',
                       'attach_type': '',
                       'client_time': None}

        # some variables
        self.parent = parent
        self.mylogger9_1 = logging.getLogger(logger_name)
        self.img_user = None
        self.img_gesture = None
        self.img_items = None
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.files = {'picture': None}
        self.dict02 = {}  # the dictionary object of the first HTTP result.
        self.mylogger9_1.info('The initialization of image-upload thread is successful.')


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
        # print('Image-upload thread begins')
        self.mylogger9_1.info('Image-upload thread begins')
        # the value of self.dict01['order_no'] is given before the run function and it is 'str' type;
        # the value of self.image is given before the run function and it is 'str' type;
        try:
            # prepare to upload the first image
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['attach_type'] = '1'
            ret, buffer = cv2.imencode('.jpg', self.img_user)
            self.files['picture'] = buffer.tostring()
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp01 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
            if resp01.status_code == 200:
                self.dict02 = json.loads(resp01.text)
                # print('Image-upload thread with type %s gets: %s' % (self.dict01['attach_type'],self.dict02))
                self.mylogger9_1.info('Image-upload thread with type %s gets %s' % (self.dict01['attach_type'],self.dict02))
            else:
                # print('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])  # E.g. 404
                self.mylogger9_1.info('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])
            # prepare to upload the second image
            self.dict01['attach_type'] = '2'
            ret, buffer = cv2.imencode('.jpg', self.img_gesture)
            self.files['picture'] = buffer.tostring()
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp02 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
            if resp02.status_code == 200:
                self.dict02 = json.loads(resp02.text)
                # print('Image-upload thread with type %s gets: %s' % (self.dict01['attach_type'],self.dict02))
                self.mylogger9_1.info('Image-upload thread with type %s gets %s' % (self.dict01['attach_type'],self.dict02))
            else:
                # print('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])  # E.g. 404
                self.mylogger9_1.info('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])
            # prepare to upload the third image
            self.dict01['attach_type'] = '3'
            ret, buffer = cv2.imencode('.jpg', self.img_items)
            self.files['picture'] = buffer.tostring()
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp03 = requests.post(self.url, headers=self.headers01, files=self.files, data=self.dict01, timeout=8)
            if resp03.status_code == 200:
                self.dict02 = json.loads(resp03.text)
                # print('Image-upload thread with type %s gets: %s' % (self.dict01['attach_type'],self.dict02))
                self.mylogger9_1.info('Image-upload thread with type %s gets %s' % (self.dict01['attach_type'],self.dict02))
            else:
                # print('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])  # E.g. 404
                self.mylogger9_1.info('Image-upload thread with type %s (end): network problem.' % self.dict01['attach_type'])
            # print('Image-upload thread ends')
            self.mylogger9_1.info('Image-upload thread ends')
        except BaseException as e:
            # self.mylogger9_1.error(e)
            self.mylogger9_1.error('-------------------------Error happens in Image-upload thread.----------------------------', exc_info=True)
            self.error.emit()


if __name__ == '__main__':
    a = MyThread9()
    a.dict01['order_no'] = 'SO201803141004214709'
    a.img_user = cv2.imread('.\\upload\\test.jpg')
    a.start()
    while a.isRunning():
        pass


