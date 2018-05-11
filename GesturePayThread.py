"""
Aim: communicating with the server to commit the order;
Main data: order number and user id;
Other data: store id, screen id and time
author = hobin;
email = '627227669@qq.com';
"""

import hashlib
import json
from datetime import datetime
import logging
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class MyThread7(QThread):
    """
    Gesture order thread
    """
    finished = pyqtSignal(object)
    finished_error = pyqtSignal()
    timeout_http = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread7, self).__init__(parent)
        self.parent = parent
        self.url = 'https://sys.commaai.cn/payment/pappay/pay'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.dict01 = {"token": None,
                       'user_id': None,
                       'order_no': None,
                       'store_id': '2',
                       'screen_id':'1',
                       'time': None}
        self.dict02 = {}  # the dictionary object of the HTTP result


    def api_sign02_hexdigest(self):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :return: the digest of the information;
        """
        input = str(self.dict01['order_no'])+str(self.dict01['user_id'])+str(self.dict01['store_id'])+str(self.dict01['screen_id'])+str(self.dict01['time'])
        # print('input', input)

        check_str = input + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.md5(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            print('Gesture order thread begins')
            self.dict01['time'] = str(int(datetime.now().timestamp()))
            self.dict01['token'] = self.api_sign02_hexdigest()
            resp01 = requests.post(self.url, data=self.dict01, timeout=3)
            self.dict02 = json.loads(resp01.text)
            print(self.dict02)
            if resp01.status_code == 200:
                if self.dict02['code'] == 200:
                    print('Gesture order thread (end): %s.' % self.dict02['msg'])
                elif self.dict02['code'] == 100:
                    self.finished_error.emit()
                    print('Gesture order thread (end): %s.' % self.dict02['msg'])
                else:
                    print('Gesture order thread (end): %s.' % self.dict02['msg'])
            else:
                print('Gesture order thread: network problem occurs.')
        except requests.exceptions.ReadTimeout:
            print('***--------------Network problem happens in gesture order thread (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except Exception as e:
            print(e)
            print('***------------------------Be careful! Error occurs in gesture order thread!------------------------***')


class MyThread7_1(QThread):
    """
    Gesture order thread
    Compared with the MyThread7 class, the logging module is introduced to this module at first time.
    Compared with the MyThread7 class, the resp01 is modified to self.resp01 to check memory leak.
    Compared with the MyThread7 class, the original header of requests is reloaded by the self.headers01 (the 'Connection' header changes from keep-alive to close);
    """
    order_success = pyqtSignal() # the initial purpose is to eliminate the magnetic of item;
    finished = pyqtSignal(object)
    finished_error = pyqtSignal()
    network_error = pyqtSignal()
    timeout_http = pyqtSignal()
    connection_error = pyqtSignal()
    error = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, url = 'https://sys.commaai.cn/payment/pappay/pay',
                 sign_key='4b111cc14a33b88e37e2e2934f493458',
                 store_id = '2', screen_id = '1', **kwargs):
        super(MyThread7_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"token": None,
                       'user_id': None,
                       'order_no': None,
                       'store_id': store_id,
                       'screen_id': screen_id,
                       'time': None}

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.url = kwargs['url']
        # self.sign_key = kwargs['sign_key']
        # self.dict01 = {"token": None,
        #                'user_id': None,
        #                'order_no': None,
        #                'store_id': kwargs['store_id'],
        #                'screen_id': kwargs['screen_id'],
        #                'time': None}

        # some variables
        self.parent = parent
        self.mylogger7_1 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the HTTP result
        self.mylogger7_1.info('The initialization of gesture order thread is successful.')


    def api_sign02_hexdigest(self):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :return: the digest of the information;
        """
        input = str(self.dict01['order_no'])+str(self.dict01['user_id'])+str(self.dict01['store_id'])+str(self.dict01['screen_id'])+str(self.dict01['time'])
        # print('input', input)

        check_str = input + self.sign_key
        # print('check_str', check_str)

        hexdigest = hashlib.md5(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

        return hexdigest


    def run(self):
        try:
            # print('Gesture order thread begins')
            self.mylogger7_1.info('Gesture order thread begins')
            self.dict01['time'] = str(int(datetime.now().timestamp()))
            self.dict01['token'] = self.api_sign02_hexdigest()
            self.mylogger7_1.info('Gesture order thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
            self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
            if self.resp01.status_code == 200:
                self.dict02 = json.loads(self.resp01.text)
                if self.dict02['code'] == 200:
                    # print('Gesture order thread (end): %s.' % self.dict02['msg'])
                    self.mylogger7_1.info('Gesture order thread (end): %s.' % self.dict02['msg'])
                    # self.order_success.emit()
                elif self.dict02['code'] == 100:
                    # print('Gesture order thread (end): %s.' % self.dict02['msg'])
                    self.mylogger7_1.info('Gesture order thread (end): %s.' % self.dict02['msg'])
                    self.finished_error.emit()
                else:
                    # print('Gesture order thread (end): %s.' % self.dict02['msg'])
                    self.mylogger7_1.info('Gesture order thread (end): %s.' % self.dict02['msg'])
            else:
                # print('Gesture order thread: network problem occurs.')
                self.mylogger7_1.info('Gesture order thread: network problem occurs.')
                self.network_error.emit()
        except requests.exceptions.ReadTimeout:
            # print('***--------------Network problem happens in gesture order thread (Timeout for the HTTP request).------------------------***')
            self.mylogger7_1.error('***--------------Network problem happens in gesture order thread (Timeout for the HTTP request).------------------------***')
            self.timeout_http.emit()
        except requests.exceptions.ConnectionError:
            self.mylogger7_1.error('***--------------Network problem happens in gesture order thread.------------------------***',exc_info=True)
            self.connection_error.emit()
        except BaseException as e:
            # self.mylogger7_1.error(e)
            self.mylogger7_1.error('***------------------------Be careful! Error occurs in gesture order thread!------------------------***',exc_info=True)
            self.error.emit()



if __name__ == '__main__':
    pass
    """
    Case one:
    {'code': 200, 
    'msg': '提交成功', 
    'time': 1517553955, 
    'data': {'return_code': 'SUCCESS', 
             'return_msg': 'OK', 
             'appid': 'wx13c6fbd6026908a1', 
             'mch_id': '1491872182', 
             'nonce_str': 'qWHAYFH01ULgdtR0', 
             'sign': '0E4275ED07AFD72A86C6306239F6EB60', 
             'result_code': 'SUCCESS'}
    }
    Case two:
    {'code': 100, 
    'msg': '获取不到用户授权信息', 
    'time': 1517554842, 
    'data': {'account_payment_order': {'code': 301, 'msg': '获取不到用户授权信息', 'time': 1517554842, 'data': []}}
    }
    Case three:
    {'code': 100, 
    'msg': '提交失败', 
    'time': 1517555237, 
    'data': {'return_code': 'SUCCESS', 
             'return_msg': 'OK', 
             'appid': 'wx13c6fbd6026908a1', 
             'mch_id': '1491872182', 
             'nonce_str': 'K8F2DVfjKCFK01oL', 
             'sign': 'EDC002FBEB8E5CAC99E684C4CD519400', 
             'result_code': 'FAIL', 
             'err_code': 'RULELIMIT', 
             'err_code_des': '交易金额或次数超出限制'}
    }
    """



