"""
QR code: Quick response code
author = hobin;
email = '627227669@qq.com';
"""
import collections
import hashlib
import json
from datetime import datetime
import logging
from memory_profiler import profile
import os
from PIL import Image
from PIL.ImageQt import ImageQt
import qrcode
import requests
from PyQt5.QtCore import QThread, pyqtSignal

from ConfiguringModule import MyConfig1
from LoggingModule import MyLogging1


class MyThread5(QThread):
    """
    It also called the order thread since the order information comes from here;
    """
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyThread5, self).__init__(parent)
        self.parent = parent
        self.url = 'http://api.commaai.cn/order/order/create_sku_order'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.dict01 = {"api_sign": None,
                       'utm_medium': 'app',
                       'utm_source': 'box',
                       'store_id': '2',
                       'screen_id':'1',
                       'client_time': None,
                       'buy_skuids': ''}
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.icon = Image.open("./Images/payment.png")
        self.icon_w, self.icon_h = self.icon.size


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


    def run(self):
        print('QRcode thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            print('QRcode thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp01 = requests.post(self.url, data=self.dict01, timeout=2)
            self.dict02 = json.loads(resp01.text)
            print('QRcode thread: new order %s' % self.dict02['data']['order_no'])
            # print(self.dict02['data']['order_link'])
            print('QRcode thread ends')
            self.finished.emit(self.make_qrcode(content=self.dict02['data']['order_link']))


class MyThread5_1(QThread):
    """
    It also called the order thread since the order information comes from here;
    Compared with the MyThread5 class, the logging module is introduced to this module at first time.
    Compared with the MyThread5 class, the resp01 is modified to self.resp01.
    """
    finished = pyqtSignal(object)

    def __init__(self, parent=None, logger_name='hobin', *, url='http://api.commaai.cn/order/order/create_sku_order',
                 sign_key= '4b111cc14a33b88e37e2e2934f493458', utm_medium='app', utm_source='box',
                 store_id = '2',screen_id= '1', **kwargs):
        super(MyThread5_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'screen_id':screen_id,
                       'client_time': None,
                       'buy_skuids': ''}

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'screen_id': kwargs['screen_id'],
        #                'client_time': None,
        #                'buy_skuids': ''}

        # some variables
        dir_path = os.path.dirname(__file__)
        icon_path = os.path.join(dir_path, 'Images', 'payment.png')
        self.parent = parent
        self.mylogger5_1 = logging.getLogger(logger_name)
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.icon = Image.open(icon_path)
        self.icon_w, self.icon_h = self.icon.size
        self.mylogger5_1.info('The initialization of QRcode thread is successful.')


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


    def run(self):
        # print('QRcode thread begins')
        self.mylogger5_1.info('QRcode thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            # print('QRcode thread ends')
            self.mylogger5_1.info('QRcode thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            self.resp01 = requests.post(self.url, data=self.dict01, timeout=8)
            self.dict02 = json.loads(self.resp01.text)
            # print('QRcode thread ends with new order %s' % self.dict02['data']['order_no'])
            self.mylogger5_1.info('QRcode thread ends with new order %s' % self.dict02['data']['order_no'])
            # print(self.dict02['data']['order_link'])
            self.finished.emit(self.make_qrcode(content=self.dict02['data']['order_link']))


class MyThread5_2(QThread):
    """
    It also called the order thread since the order information comes from here;
    Compared with the MyThread5 class, the logging module is introduced to this module at first time.
    Compared with the MyThread5 class, the resp01 is modified to self.resp01.
    Compared with the MyThread5_1 class, 'try...except...' is added for 'self.resp01 = requests.post()'.
    """
    finished = pyqtSignal(object)
    timeout_network = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, url='http://api.commaai.cn/order/order/create_sku_order',
                 sign_key= '4b111cc14a33b88e37e2e2934f493458', utm_medium='app', utm_source='box',
                 store_id = '2',screen_id= '1', **kwargs):
        super(MyThread5_2, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'screen_id':screen_id,
                       'client_time': None,
                       'buy_skuids': ''}

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'screen_id': kwargs['screen_id'],
        #                'client_time': None,
        #                'buy_skuids': ''}

        # some variables
        dir_path = os.path.dirname(__file__)
        icon_path = os.path.join(dir_path, 'Images', 'payment.png')
        self.parent = parent
        self.mylogger5_2 = logging.getLogger(logger_name)
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.icon = Image.open(icon_path)
        self.icon_w, self.icon_h = self.icon.size
        self.mylogger5_2.info('The initialization of QRcode thread is successful.')


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


    def run(self):
        # print('QRcode thread begins')
        self.mylogger5_2.info('QRcode thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            # print('QRcode thread ends')
            self.mylogger5_2.info('QRcode thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            try:
                self.resp01 = requests.post(self.url, data=self.dict01, timeout=8)
                self.dict02 = json.loads(self.resp01.text)
                # print('QRcode thread ends with new order %s' % self.dict02['data']['order_no'])
                self.mylogger5_2.info('QRcode thread ends with new order %s' % self.dict02['data']['order_no'])
                # print(self.dict02['data']['order_link'])
                self.finished.emit(self.make_qrcode(content=self.dict02['data']['order_link']))
            except BaseException:
                self.mylogger5_2.error('***------------------------Be careful! Error occurs in QRcode thread!------------------------***', exc_info=True)
                self.timeout_network.emit()


class MyThread5_3(QThread):
    """
    It also called the order thread since the order information comes from here;
    Compared with the MyThread5 class, the logging module is introduced to this module at first time.
    Compared with the MyThread5 class, the resp01 is modified to self.resp01.
    Compared with the MyThread5_1 class, 'try...except...' is added for 'self.resp01 = requests.post()'.
    Compared with the MyThread5_2 class, this class does not need to emit the QR code and it emits self.post_order_success in stead..
    Compared with the MyThread5_2 class, the original header of requests is reloaded by the self.headers01 (the 'Connection' header changes from keep-alive to close);
    """
    finished = pyqtSignal(object)
    timeout_network = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, url='http://api.commaai.cn/order/order/create_sku_order',
                 sign_key= '4b111cc14a33b88e37e2e2934f493458', utm_medium='app', utm_source='box',
                 store_id = '2',screen_id= '1', **kwargs):
        super(MyThread5_3, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'screen_id':screen_id,
                       'client_time': None,
                       'buy_skuids': ''}

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'screen_id': kwargs['screen_id'],
        #                'client_time': None,
        #                'buy_skuids': ''}

        # some variables
        self.parent = parent
        self.mylogger5_3 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.post_order_success = False
        self.mylogger5_3.info('The initialization of Order thread is successful.')


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
        self.mylogger5_3.info('Order thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        self.post_order_success = False
        if len(self.dict01['buy_skuids']) == 0:
            self.mylogger5_3.info('Order thread ends')
            self.finished.emit(self.post_order_success)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            try:
                self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
                # self.mylogger5_3.info('The header information of first request is %s' %self.resp01.request.headers)
                # self.mylogger5_3.info('The header information of first response is %s' % self.resp01.headers)
                self.dict02 = json.loads(self.resp01.text)
                self.mylogger5_3.info('Order thread ends with new order %s' % self.dict02['data']['order_no'])
                self.post_order_success = True
                self.finished.emit(self.post_order_success)
            except requests.exceptions.ReadTimeout:
                self.mylogger5_3.error('***------------------------Be careful! Error occurs in Order thread!------------------------***', exc_info=True)
                self.timeout_network.emit()
            except BaseException:
                self.mylogger5_3.error('***------------------------Be careful! Error occurs in Order thread!------------------------***',exc_info=True)
                self.error.emit()


class MyThread5_3_1(QThread):
    """
    It also called the order thread since the order information comes from here;
    Compared with the MyThread5 class, the logging module is introduced to this module at first time.
    Compared with the MyThread5 class, the resp01 is modified to self.resp01.
    Compared with the MyThread5_1 class, 'try...except...' is added for 'self.resp01 = requests.post()'.
    Compared with the MyThread5_2 class, this class does not need to emit the QR code and it emits self.post_order_success in stead..
    Compared with the MyThread5_2 class, the original header of requests is reloaded by the self.headers01 (the 'Connection' header changes from keep-alive to close);
    Compared with the MyThread5_3 class, this class emit the order_link instead after successful post;
    Compared with the MyThread5_3 class, this class will take care of the status code when it is not 200;
    """
    finished = pyqtSignal(object)
    order_error = pyqtSignal()
    timeout_network = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, url='http://api.commaai.cn/order/order/create_sku_order',
                 sign_key= '4b111cc14a33b88e37e2e2934f493458', utm_medium='app', utm_source='box',
                 store_id = '2',screen_id= '1', **kwargs):
        super(MyThread5_3_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'screen_id': screen_id,
                       'client_time': None,
                       'buy_skuids': ''}

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.dict01 = {"api_sign": None,
        #                'utm_medium': kwargs['utm_medium'],
        #                'utm_source': kwargs['utm_source'],
        #                'store_id': kwargs['store_id'],
        #                'screen_id': kwargs['screen_id'],
        #                'client_time': None,
        #                'buy_skuids': ''}

        # some variables
        self.parent = parent
        self.mylogger5_3_1 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.post_order_success = False
        self.mylogger5_3_1.info('The initialization of Order thread is successful.')


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
        self.mylogger5_3_1.info('Order thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            self.mylogger5_3_1.info('Order thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            try:
                self.mylogger5_3_1.info('Order thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
                self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
                # self.mylogger5_3_1.info('The header information of first request is %s' %self.resp01.request.headers)
                # self.mylogger5_3_1.info('The header information of first response is %s' % self.resp01.headers)
                if self.resp01.status_code == 200:
                    self.dict02 = json.loads(self.resp01.text)
                    self.mylogger5_3_1.info('Order thread ends with new order %s' % self.dict02['data']['order_no'])
                    self.finished.emit(self.dict02['data']['order_link'])
                else:
                    self.mylogger5_3_1.error('Order thread (ends): ---------the status code of the response is not 200 in Order thread---------')
                    self.order_error.emit()

            except requests.exceptions.ReadTimeout:
                self.mylogger5_3_1.error('***------------------------Be careful! Error occurs in Order thread!------------------------***', exc_info=True)
                self.timeout_network.emit()
            except BaseException:
                self.mylogger5_3_1.error('***------------------------Be careful! Error occurs in Order thread!------------------------***',exc_info=True)
                self.error.emit()


class MyThread5_3_1_1(QThread):
    """
    Compared with the MyThread5_3_1 class, this class adds extra parameters into self.dict01:
    system_version, api_ver, device_id, csp_id, weight, client_ip
    """
    finished = pyqtSignal(object)
    order_error = pyqtSignal()
    timeout_network = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent=None, client_ip='127.0.0.1', logger_name='hobin', *, url='http://api.commaai.cn/order/order/create_sku_order',
                 sign_key= '4b111cc14a33b88e37e2e2934f493458', utm_medium='app', utm_source='box',
                 store_id = '2',screen_id= '1', system_version='ubuntu', api_ver='2.0',
                 device_id='cmbox', csp_id='cashier_0001', **kwargs):
        super(MyThread5_3_1_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'store_id': store_id,
                       'screen_id': screen_id,
                       'system_version': system_version,
                       'api_ver': api_ver,
                       'device_id': device_id,
                       'csp_id': csp_id,
                       'client_time': None,
                       'weight': None,
                       'buy_skuids': '',
                       'client_ip': client_ip}

        # some variables
        self.parent = parent
        self.mylogger5_3_1_1 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.post_order_success = False
        self.mylogger5_3_1_1.info('The initialization of Order thread is successful.')


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
        self.mylogger5_3_1_1.info('Order thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            self.mylogger5_3_1_1.info('Order thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            try:
                self.mylogger5_3_1_1.info('Order thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
                self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
                self.mylogger5_3_1_1.info('The header information of first request is %s' %self.resp01.request.headers)
                # self.mylogger5_3_1_1.info('The header information of first response is %s' % self.resp01.headers)
                if self.resp01.status_code == 200:
                    self.mylogger5_3_1_1.info('The data of response is %s' % self.resp01.text)
                    self.dict02 = json.loads(self.resp01.text)
                    self.mylogger5_3_1_1.info('Order thread ends with new order %s' % self.dict02['data']['order_no'])
                    self.finished.emit(self.dict02['data']['order_link'])
                else:
                    self.mylogger5_3_1_1.error('Order thread (ends): ---------the status code of the response is not 200 in Order thread---------')
                    self.order_error.emit()

            except requests.exceptions.ReadTimeout:
                self.mylogger5_3_1_1.error('***------------------------Be careful! Error occurs in Order thread!------------------------***', exc_info=True)
                self.timeout_network.emit()
            except BaseException:
                self.mylogger5_3_1_1.error('***------------------------Be careful! Error occurs in Order thread!------------------------***',exc_info=True)
                self.error.emit()


class MyThread5_T1(MyThread5):
    """
    It also called the order thread since the order information comes from here;
    It is monitored by memory_profile to check the memory leak.
    """
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyThread5_T1, self).__init__(parent)


    @profile(precision=2)
    def run(self):
        print('QRcode thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            print('QRcode thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp01 = requests.post(self.url, data=self.dict01, timeout=1)
            self.dict02 = json.loads(resp01.text)
            print('QRcode thread: new order %s' % self.dict02['data']['order_no'])
            # print(self.dict02['data']['order_link'])
            print('QRcode thread ends')
            self.finished.emit(self.make_qrcode(content=self.dict02['data']['order_link']))


class MyThread5_T2(MyThread5):
    """
    It also called the order thread since the order information comes from here;
    It is monitored to check the memory leak and the resp01 is modified to self.resp01
    """
    finished = pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyThread5_T2, self).__init__(parent)
        self.resp01 = None


    @profile(precision=2)
    def run(self):
        print('QRcode thread begins')
        # the value of self.dict01['buy_skuids'] is given before the run function and it is 'str' type;
        # Currently, it is given after the completion of the sql thread;
        if len(self.dict01['buy_skuids']) == 0:
            print('QRcode thread ends')
            self.finished.emit(None)
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            self.resp01 = requests.post(self.url, data=self.dict01, timeout=1)
            self.dict02 = json.loads(self.resp01.text)
            print('QRcode thread: new order %s' % self.dict02['data']['order_no'])
            # print(self.dict02['data']['order_link'])
            print('QRcode thread ends')
            self.finished.emit(self.make_qrcode(content=self.dict02['data']['order_link']))


if __name__ == '__main__':
    a = MyThread5_3_1()
    a.dict01['buy_skuids'] = '148,148'
    counter = 1
    while counter > 0:
        a.start()
        while a.isRunning():
            pass
        counter = counter - 1

    # configuration
    myconfig = MyConfig1(cfg_path='Klas2_Singtel_normal.cfg')
    # logging
    mylogging = MyLogging1(logger_name='hobin')

    b = MyThread5_3_1_1(client_ip= '192.168.10.139',**myconfig.data['order'])
    b.dict01['buy_skuids'] = '1'
    b.start()
    while b.isRunning():
        pass


