"""
QR code: Quick response code
author = hobin
"""
import collections
import hashlib
import json
from datetime import datetime

from PIL import Image
from PIL.ImageQt import ImageQt
import qrcode
import requests
from PyQt5.QtCore import QThread, pyqtSignal


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
        self.icon = Image.open("./images/payment.png")
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
            resp01 = requests.post(self.url, data=self.dict01, timeout=1)
            self.dict02 = json.loads(resp01.text)
            # print(self.dict02['data']['order_link'])
            print('QRcode thread ends')
            self.finished.emit(self.make_qrcode(content=self.dict02['data']['order_link']))


if __name__ == '__main__':
    a = MyThread5()
    a.dict01['buy_skuid'] = '148,148'
    a.start()
    while a.isRunning():
        pass

