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
import pyzbar.pyzbar as pyzbar

class MyThread10(QThread):
    network_error = pyqtSignal()

    def __init__(self, parent=None, logger_name='hobin', *, url = 'http://api.zhy.commaai.cn/order/attach/upload_goods_qrcode',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', utm_medium = 'app', utm_source = 'box', **kwargs):
        super(MyThread10, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.url = url
        self.sign_key = sign_key
        self.dict01 = {"api_sign": None,
                       'utm_medium': utm_medium,
                       'utm_source': utm_source,
                       'order_no': '',
                       'qrdata_list': '',
                       'client_time': None
                       }

        # some variables
        self.frame = None
        self.parent = parent
        self.not_retry = True
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}

        self.mylogger10 = logging.getLogger(logger_name)
        self.mylogger10.info('The initialization of item-quality thread is successful.')

    def run(self):
        self.mylogger10.info('item-quality thread begins')
        # the order_no is passed from the outside
        if self.not_retry:
            info_list = self.detect(self.frame)
            # print(type(info_list[0]))  # the data type is bytes;
            info_list_str = ''
            for item in info_list:
                info_list_str = info_list_str + str(item, 'ascii') + ','
            if len(info_list) > 0:
                self.dict01['qrdata_list'] = info_list_str[:-1]
            else:
                self.dict01['qrdata_list'] = ''
            # print(self.dict01['qrdata_list'])
            self.dict01['client_time'] = str(int(datetime.now().timestamp()))
            self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
        try:
            self.mylogger10.info('item-quality thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
            self.resp01 = requests.post(self.url, headers=self.headers01, data=self.dict01, timeout=8)
            if self.resp01.status_code == 200:
                self.dict02 = json.loads(self.resp01.text)
                self.not_retry = True
                self.mylogger10.info('item_quality ends with %s' % self.dict02)
            else:
                self.mylogger10.info('Item-quality thread: ---------the status code of the response is not 200 in Order thread---------')
                self.not_retry = False
                self.network_error.emit()
        except BaseException:
            self.mylogger10.error('-------------------------Error happens in Item-quality thread.----------------------------', exc_info=True)
        self.mylogger10.info('item-quality thread ends')

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

    def detect(self, image):
        copyimg = image.copy()
        sp = image.shape
        width = sp[1]
        height = sp[0]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_G = cv2.GaussianBlur(gray, (5, 5), 0)

        gradX = cv2.Sobel(blurred_G, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradY = cv2.Sobel(blurred_G, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)

        gradient = cv2.subtract(gradX, gradY)
        gradient = cv2.convertScaleAbs(gradient)

        blurred = cv2.blur(gradient, (9, 9))
        (_, thresh) = cv2.threshold(blurred, 195, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        # cv2.imwrite('/home/qiu/mark/closed_0.jpg',closed)

        closed = cv2.erode(closed, kernel, iterations=2)
        closed = cv2.dilate(closed, kernel, iterations=2)
        # cv2.imwrite('/home/qiu/mark/closed_1.jpg', closed)

        image, cnts, hierarchy = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        n = len(cnts)
        data1 = []

        if n > 35:
            n = 35

        cc = 0
        for i in range(n):
            x, y, w, h = cv2.boundingRect(cnts[i])
            x1 = x - w
            y1 = y - h
            w1 = w + 2 * w
            h1 = h + 2 * h
            xmax = x + w
            ymax = y + h
            xmax1 = x1 + w1
            ymax1 = y1 + h1

            if w * h > 100000:
                y1 = y - 20
                x1 = x - 20
                xmax1 = x + w + 20
                ymax1 = y + h + 20

            if (xmax1 > width):
                xmax1 = width
            if (ymax1 > height):
                ymax1 = height
            if (x1 < 0):
                x1 = 0
            if (y1 < 0):
                y1 = 0
            imgROI1 = copyimg[y:ymax, x:xmax]  # small
            imgROI = copyimg[y1:ymax1, x1:xmax1]  # big

            # cv2.imwrite('/home/qiu/mark/file_%d.jpg' % i, imgROI)

            for j in range(-5, 5):
                percentage = 1.0 + 0.02 * j
                data = self.recognition_qr(imgROI, imgROI1, i, percentage, 2)
                if (data != None):
                    # cv2.imwrite('/home/qiu/mark/final_%d.jpg' % cc, imgROI1)
                    cc += 1
                    data1.append(data)
                    break

        data_set = list(set(data1))
        # data_set = data1
        return data_set

    def recognition_qr(self, img, img1, i, percent, kernel):

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
        img = cv2.blur(img, (kernel, kernel))
        (ret, _) = cv2.threshold(img1, 0, 255, cv2.THRESH_OTSU)
        ret = ret * percent
        (_, thresh) = cv2.threshold(img, ret, 255, cv2.THRESH_BINARY)

        decodeObjects = pyzbar.decode(thresh)
        if not decodeObjects == []:
            return decodeObjects[0].data
        else:
            return None


if __name__ == '__main__':
    a = MyThread10()
    a.dict01['order_no'] = 'SO201805041012421019'
    a.frame = cv2.imread('./Images/20180505013200.jpg')
    a.start()
    while a.isRunning():
        pass

