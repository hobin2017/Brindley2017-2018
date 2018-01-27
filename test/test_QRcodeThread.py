"""
QR code: Quick response code
"""
import collections
import hashlib
import json
from datetime import datetime

import qrcode
import requests
from PIL import Image
from PyQt5.QtCore import QThread


class Mythread5(QThread):
    """

    """
    def __init__(self, parent=None):
        super(Mythread5, self).__init__(parent)
        self.parent = parent
        self.url = 'http://api.commaai.cn/order/order/create_sku_order'
        self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
        self.dict01 = {"api_sign": None,
                       'utm_medium': 'app',
                       'utm_source': 'box',
                       'store_id': '2',
                       'screen_id':'1',
                       'client_time': None,
                       'buy_skuids':None,}
        self.dict02 = {}  # the dictionary object of the first HTTP result


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
        print('QRcode thread begins')
        self.dict01['buy_skuids'] = '567'
        self.dict01['client_time'] = str(int(datetime.now().timestamp()))
        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
        resp01 = requests.post(self.url, data=self.dict01, timeout=1)
        self.dict02 = json.loads(resp01.text)
        print(self.dict02['data']['order_link'])
        # the first way to create the QR code
        img1 = qrcode.make(self.dict02['data']['order_link'])
        img1.save('paymentCode1.png')
        # generating QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=4)
        qr.add_data(self.dict02['data']['order_link'])
        qr.make(fit=True)  # to avoid data overflow errors
        img2 = qr.make_image()
        img2 = img2.convert("RGBA")
        # adding the image to the QR code
        icon = Image.open("./images/payment.png")
        img2_w, img2_h = img2.size
        factor = 4
        size_w = int(img2_w / factor)
        size_h = int(img2_h / factor)
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
        w = int((img2_w - icon_w) / 2)
        h = int((img2_h - icon_h) / 2)
        # icon = icon.convert("RGBA")
        img2.paste(icon, (w, h), icon)
        img2.save('paymentCode2.png')  # saving the QR code with a image inside it


if __name__ == '__main__':
    a = Mythread5()
    a.start()
    while a.isRunning():
        pass

