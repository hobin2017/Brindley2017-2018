"""
Aim: communicating with the server to commit the order;
Main data: order number and user id;
Other data: store id, screen id and time
author = hobin
"""

import collections
import hashlib
import json
from datetime import datetime

import requests
from PyQt5.QtCore import QThread, pyqtSignal

class MyThread5(QThread):
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


    def api_sign_hexdigest(self, dict):
        """
        It is used to produce the digest of the information;
        The rule is specified in 'check_str';
        :param dict: the dictionary data which will be passed to the server;
        :return: the digest of the information;
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
        if len(self.dict01['buy_skuids']) == 0:
            print('No need to post the order since the customer buys nothing')
        else:
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
            resp01 = requests.post(self.url, data=self.dict01, timeout=1)
            print(resp01.text)
            self.dict02 = json.loads(resp01.text)
            print('new order number is', self.dict02['data']['order_no'])


class MyThread7(QThread):
    """
    Gesture order thread
    """
    finished = pyqtSignal(object)

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
        print('Gesture order thread begins')
        self.dict01['time'] = str(int(datetime.now().timestamp()))
        self.dict01['token'] = self.api_sign02_hexdigest()
        resp01 = requests.post(self.url, data=self.dict01, timeout=1)
        self.dict02 = json.loads(resp01.text)
        print(self.dict02)
        if resp01.status_code == 200:
            if self.dict02['code'] == '200':
                print('Gesture order thread (end): %s.' % self.dict02['msg'])
            else:
                print('Gesture order thread (end): %s.' % self.dict02['msg'])
        else:
            print('Gesture order thread: network problem occurs.')


if __name__ == '__main__':
    a = MyThread5()
    a.dict01['buy_skuids'] = '148,148,148,148,148'
    a.start()
    while a.isRunning():
        pass
    print('--------try to submit the order----------------')
    b = MyThread7()
    b.dict01['user_id'] = '3503'  # 3503, 3858
    b.dict01['order_no'] = a.dict02['data']['order_no']
    b.start()
    while b.isRunning():
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


