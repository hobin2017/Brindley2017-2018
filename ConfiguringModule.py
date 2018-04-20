# -*- coding: utf-8 -*-
"""
Aim: all parameters which might be modified, go to one place.
author: hobin
"""
import configparser


class MyConfig1(object):
    """
    The configuration information comes from one file and the result is one dictionary.
    One disadvantage is that it is hard to pass a list by this way.
    """
    def __init__(self, cfg_path='Klas2.cfg'):
        self.data = {}
        cf = configparser.ConfigParser()
        cf.read(cfg_path)
        # 1, Loading all section data into one dictionary .
        for section in cf.sections():
            self.data[section] = {}
            for item in cf.options(section):
                self.data[section][item] = cf.get(section, item)

        # 2, Loading all data into one dictionary.
        # for section in cf.sections():
        #     for item in cf.options(section):
        #         self.data[item] = cf.get(section, item)


class MyConfig2(object):
    """
    a collection of dictionaries and lists.
    It is not friendly for user who has no computer science background.
    """
    def __init__(self):
        self.dict = {}
        #
        self.dict['camera'] = {
            'cam_user': '0',
            'cam_item': '1'
        }
        # for account thread
        self.dict['accout'] = {
            'url' : 'http: // api.commaai.cn // v1 / face / find_user',
            'sign_key' : '4b111cc14a33b88e37e2e2934f493458',
            'store_id' : '2',
            'utm_medium' : 'app',
            'utm_source' : 'box',
            'face_classifer_path': 'C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml'
        }

        # for gesture_pay thread
        self.dict['gesture_pay'] = {
            'url' : 'https: // sys.commaai.cn / payment / pappay / pay',
            'sign_key' : '4b111cc14a33b88e37e2e2934f493458',
            'store_id' : '2',
            'screen_id' : '1'
        }

        # for image_upload thread
        self.dict['image_upload'] = {
            'url' : 'http: // api.commaai.cn / order / attach / upload_payment_attach',
            'sign_key' : '4b111cc14a33b88e37e2e2934f493458',
            'utm_medium' : 'app',
            'utm_source' : 'box'
        }

        # ml_hand
        self.dict['ml_hand'] = {
            'PATH_TO_CKPT' : 'D:\\01PythonFile\\tensorflow\\models - master\\research\\object_detection\\hand_rfcn_resnet101out\\output_inference_graph.pb\\frozen_inference_graph.pb',
        'PATH_TO_LABELS' : 'D:\\01PythonFile\\tensorflow\\models - master\\research\\object_detection\\data\\hand_label_map.pbtxt',
        'NUM_CLASSES' : 3
        }

        # ml_item
        self.dict['ml_hand'] = {
            'PATH_TO_CKPT': 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\frozen_inference_graph.pb',
            'PATH_TO_LABELS': 'D:\\01PythonFile\\Brindley\\object_detection\\output_inference_graph.pb\\pascal_label_map.pbtxt',
            'NUM_CLASSES': 25
        }

        # order thread
        self.dict['order'] = {
            'url' : 'http: // api.commaai.cn / order / order / create_sku_order',
        'sign_key' : '4b111cc14a33b88e37e2e2934f493458',
        'utm_medium' : 'app',
        'utm_source' : 'box',
        'store_id' : 2,
        'screen_id' : 1,
        }

        #
        self.dict['db'] = {
            'db_port' : 3306,
        'db_host' : '127.0.0.1',
        'db_user' : 'root',
        'db_pass' : 'commaai2017',
        'db_database' : 'hobin'
        }

        #
        self.dict['user_tracking'] = {
            'face_classifer_path' : 'C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
            'eyes_classifer_path' : 'C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_eye.xml'
        }

        #
        self.dict['websocket'] = {
            'socketUrl' : 'http: // sys.commaai.cn',
            'socketPort' : 60000,
            'storeName' : 'development center for testing',
            'storeId' : '2',
            'screenId' : '1'
        }



if __name__ == '__main__':
    a = MyConfig1()
    for item in a.data:
        print(a.data[item])
    print('-------------------------------')
    print(a.data)