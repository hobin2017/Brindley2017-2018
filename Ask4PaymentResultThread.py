# -*- coding: utf-8 -*-
"""
For more information, please visit the link: https://pay.weixin.qq.com/wiki/doc/api/native.php?chapter=9_2
"""
import json
import logging

import requests
import time
from PyQt5.QtCore import QThread, pyqtSignal

from LoggingModule import MyLogging1


class Ask4PaymentResultThread01(QThread):

    pay_clear_order = pyqtSignal(object)  # order number

    def __init__(self, parent=None, logger_name='hobin', *,
                 url='https://sys.zhy.commaai.cn/payment/index/related_query', **kwargs):
        super().__init__()
        self.url = url
        self.dict01 = {'related_no': None,
                       'pay_model': None}  # pay_model: 2 indicates gesture-pay, 1 is QR code;

        # some variables
        self.parent = parent
        self.mylogger_asking_payment_result01 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger_asking_payment_result01.info('The initialization of Ask4PaymentResult thread is successful.')


    def run(self):
        self.mylogger_asking_payment_result01.info('--------------Ask4PaymentResultThread begins----------------------')
        try:
            self.mylogger_asking_payment_result01.info('Ask4PaymentResultThread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
            self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
            self.mylogger_asking_payment_result01.info('The header information of first request is %s' % self.resp01.request.headers)
            self.mylogger_asking_payment_result01.info('The header information of first response is %s' % self.resp01.headers)
            if self.resp01.status_code == 200:
                self.dict02 = json.loads(self.resp01.text)
                self.mylogger_asking_payment_result01.info('Ask4PaymentResultThread: the response of server is %s' %self.dict02)
                if self.dict02['code'] == 200:
                    # The data is available if the 'code' value returned by server is 200
                    if self.dict02['data']['result_code'] == 'SUCCESS':
                        if self.dict02['data']['trade_state'] == 'SUCCESS':
                            # the trade_state only exist if result_code=SUCCESS
                            self.pay_clear_order.emit(self.dict02['data']['out_trade_no'])
                else:
                    self.mylogger_asking_payment_result01.info('Ask4PaymentResultThread: ---------the error of server logical part happens---------')
            else:
                self.mylogger_asking_payment_result01.error('Ask4PaymentResultThread: ---------the status code of the response is not 200---------')
        except BaseException:
            self.mylogger_asking_payment_result01.error('***------------------------Be careful! Error occurs in Ask4PaymentResultThread!------------------------***',exc_info=True)

        self.mylogger_asking_payment_result01.info('--------------Ask4PaymentResultThread ends----------------------')


class Ask4PaymentResultThread02(QThread):
    """
    Compared with the Ask4PaymentResultThread01 class, one main difference is the while loop in its run();
    The second difference is the sleeping before the while loop since the order is valid when the QR code is scanned;
    The third difference is the logic part to emit the pay_clear_order signal;
    """
    pay_clear_order = pyqtSignal(object)  # order number

    def __init__(self, parent=None, logger_name='hobin', *,
                 url='https://sys.zhy.commaai.cn/payment/index/related_query', **kwargs):
        super().__init__()
        self.url = url
        self.dict01 = {'related_no': None,
                       'pay_model': None}  # pay_model: 2 indicates gesture-pay, 1 is QR code;

        # some variables
        self.parent = parent
        self.status = True
        self.asking_payment_result_interval = 6  # unit: second
        self.mylogger_asking_payment_result02 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger_asking_payment_result02.info('The initialization of Ask4PaymentResult thread is successful.')


    def run(self):
        self.status = True
        time.sleep(self.asking_payment_result_interval)  # It is only good for the qrcode payment and it seems to be useless for gesture-pay payment
        try:
            while self.status:
                self.mylogger_asking_payment_result02.info('--------------Ask4PaymentResultThread begins----------------------')
                # self.mylogger_asking_payment_result02.info('Ask4PaymentResultThread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
                self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
                # self.mylogger_asking_payment_result02.info('The header information of first request is %s' % self.resp01.request.headers)
                # self.mylogger_asking_payment_result02.info('The header information of first response is %s' % self.resp01.headers)
                if self.resp01.status_code == 200:
                    self.dict02 = json.loads(self.resp01.text)
                    self.mylogger_asking_payment_result02.info('Ask4PaymentResultThread: the response of server is %s' % self.dict02)
                    if self.dict02['code'] == 200:
                        if self.dict02['data']['result_code'] == 'SUCCESS':
                            if self.dict02['data']['trade_state'] == 'SUCCESS':
                                self.status = False
                                self.mylogger_asking_payment_result02.info('Ask4PaymentResultThread (end): the payment is %s' %self.dict02['data']['trade_state'])
                                self.pay_clear_order.emit(self.dict02['data']['out_trade_no'])
                            else:
                                self.mylogger_asking_payment_result02.info('Ask4PaymentResultThread (end): the payment is %s' %self.dict02['data']['trade_state'])
                                time.sleep(self.asking_payment_result_interval)
                        else:
                            self.mylogger_asking_payment_result02.info('Ask4PaymentResultThread (end): result_code=%s' %self.dict02['data']['result_code'])
                            time.sleep(self.asking_payment_result_interval)
                    else:
                        self.mylogger_asking_payment_result02.info('Ask4PaymentResultThread (end): ---------the error of server logical part happens---------')
                else:
                    self.mylogger_asking_payment_result02.error('Ask4PaymentResultThread (end): ---------the status code of the response is not 200---------')
            self.mylogger_asking_payment_result02.info('--------------Ask4PaymentResultThread ends----------------------')
        except BaseException:
            self.mylogger_asking_payment_result02.error('***------------------------Be careful! Error occurs in Ask4PaymentResultThread!------------------------***',exc_info=True)


if __name__ == '__main__':
    mylogging = MyLogging1(logger_name='hobin')
    initial_instance = Ask4PaymentResultThread01()
    initial_instance.dict01['pay_model'] = 2
    initial_instance.dict01['related_no'] = 'SO201809131539359816'
    initial_instance.start()
    while initial_instance.isRunning():
        pass
    # --------------------------------------------------------------------------------------------------------
    # mylogging = MyLogging1(logger_name='hobin')
    initial_instance = Ask4PaymentResultThread02()
    initial_instance.dict01['pay_model'] = 2
    initial_instance.dict01['related_no'] = 'SO201809131539359816'
    initial_instance.start()
    while initial_instance.isRunning():
        pass
