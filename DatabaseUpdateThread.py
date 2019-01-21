# -*- coding: utf-8 -*-
"""

"""
import collections
import hashlib
import json
import logging
import pdb

import mysql.connector
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from datetime import datetime

from PyQt5.QtGui import QPixmap

from LoggingModule import MyLogging1

class skuDownloadThread01(QThread):
    """
    to update the sku information for the local database
    The weight value is originally retrieved from the 'goods_weight' column of storegoods table.
    By now, the weight value
    """
    error_database_connection = pyqtSignal()
    update_images_dict = pyqtSignal(object, object)  # sku_id, image data
    finish_with_sku = pyqtSignal(object)  # a str written in special rules

    def __init__(self, parent=None, client_ip='127.0.0.1', logger_name='hobin', *, utm_medium='cashier', utm_source='cmbox_cm002',
                 sign_key='4b111cc14a33b88e37e2e2934f493458', url_sku_dwonload ='https://api.lang.commaretail.com/cashier/cv_sync/sku_dwonload',
                 store_id='2', screen_id='5', system_version='windows', api_ver='1.0', device_id='cashier',
                 csp_id='cashier_0001', db_user='root', db_pass='qwerQWER', db_database='hobin', db_port='3306',
                 db_host='127.0.0.1', **kwargs):
        super().__init__(parent)
        # for http request
        self.url_sku_dwonload = url_sku_dwonload
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
                       'client_ip': client_ip}

        # for database
        self.mysql_config = {
            'user': db_user,
            'password': db_pass,
            'port': int(db_port),
            'host': db_host,
            'database': db_database
        }
        self.conn = mysql.connector.connect(**self.mysql_config)
        # I does not add the store_id condition in where clause since I want a identical cv_id.
        self.sql_query_before_insert = 'select * from storegoods where cv_id = %s'
        self.sql_delete = 'delete from storegoods where cv_id = %s'
        self.sql_insert = """
        insert into storegoods (store_id, goods_name, goods_spec, sku_price, sku_id, goods_weight, cv_id)
        values (%s, %s, %s, %s, %s, %s, %s)
        """

        # some variables
        self.parent = parent
        self.item_images_path = './item_images/'
        self.store_id = store_id
        self.mylogger_sku_download01 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.resp02 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.dict03 = {} # the dictionary object of the second HTTP result
        self.mylogger_sku_download01.info('The initialization of skuDownload thread is successful.')


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
        self.mylogger_sku_download01.info('skuDownload thread begins')
        self.dict01['client_time'] = str(int(datetime.now().timestamp()))
        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
        try:
            self.mylogger_sku_download01.info('skuDownload thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
            self.resp01 = requests.post(self.url_sku_dwonload, headers=self.headers01, data=self.dict01, timeout=8)
            self.mylogger_sku_download01.info('The data information of first response is %s' % self.resp01.text)
            self.mylogger_sku_download01.info('The header information of first request is %s' %self.resp01.request.headers)
            self.mylogger_sku_download01.info('The header information of first response is %s' % self.resp01.headers)
            if self.resp01.status_code == 200:
                self.dict02 = json.loads(self.resp01.text)
                if self.dict02['code'] == 200:
                    # the useful data
                    # self.dict02['data']['list'] is a list of dict.
                    # the items of every dict are: ('cv_id', int), ('sku_barcode', None), ('goods_spec', str),
                    # ('packing_num', int), ('goods_id', int), ('sku_price', str), ('langguage_pack', a list of dict),
                    # ('goods_image', str), ('packing_units', str), ('sku_code', str), ('sku_id', int),
                    # ('sku_weight', int), ('goods_name', str), ('sku_name', str).
                    # self.mylogger_sku_download01.info(self.dict02['data']['lists'])
                    updated_sku_str = ''
                    self.conn.close()
                    self.conn = mysql.connector.connect(**self.mysql_config)
                    cursor = self.conn.cursor()
                    for index, item in enumerate(self.dict02['data']['lists']):
                        self.mylogger_sku_download01.info('new item with %s is %s' %(index, item))
                        # self.mylogger_sku_download01.info('the keys of the new item is %s' %item.keys())
                        cursor.execute(self.sql_query_before_insert, (item['cv_id'],))
                        result_before_insert = cursor.fetchall()
                        # self.mylogger_sku_download01.info(result_before_insert)  # it might be a empty list.
                        if result_before_insert:
                            cursor.execute(self.sql_delete, (item['cv_id'],))
                        cursor.execute(self.sql_insert, (self.store_id, item['goods_name'], item['goods_spec'],
                                                         item['sku_price'], item['sku_id'], item['sku_weight'],
                                                         item['cv_id']))
                        # cursor.execute('select * from storegoods where store_id = %s and cv_id = %s', (self.store_id, item['cv_id']))
                        # self.mylogger_sku_download01.info(cursor.fetchall())  # the result is newest even you does not commit.
                        updated_sku_str = updated_sku_str + '%s,' % item['sku_id']
                        #
                        self.resp02 = requests.get(item['goods_image'])
                        if self.resp02.status_code == 200:
                            with open(self.item_images_path + '%s.jpg' % item['sku_id'], 'wb') as f:
                                f.write(self.resp02.content)
                            self.update_images_dict.emit(item['sku_id'], self.resp02.content)
                        else:
                            self.mylogger_sku_download01.info('skuDownload thread: ---------the status code of the second response is not 200---------')
                    cursor.close()
                    self.conn.commit()  # you need to commit it otherwise the local database is not updated.
                    self.conn.close()
                    updated_sku_str = updated_sku_str[:-1]
                    if updated_sku_str:
                        self.finish_with_sku.emit(updated_sku_str)
                else:
                    self.mylogger_sku_download01.error('skuDownload thread: ---------the error of server logical part happens---------')
            else:
                self.mylogger_sku_download01.error('skuDownload thread: ---------the status code of the response is not 200---------')

        except requests.exceptions.ReadTimeout:
            self.mylogger_sku_download01.error('***------------------------Be careful! Error occurs in skuDownload thread!------------------------***',exc_info=True)
        except mysql.connector.Error:
            self.mylogger_sku_download01.error('***------------------------Be careful! Error occurs in SQL thread!------------------------***',exc_info=True)
            self.conn.close()
            self.conn = mysql.connector.connect(**self.mysql_config)
            self.error_database_connection.emit()
        except BaseException:
            self.mylogger_sku_download01.error('***------------------------Be careful! Error occurs in skuDownload thread!------------------------***',exc_info=True)
        self.mylogger_sku_download01.info('skuDownload thread ends')


class skuDownloadFinishedThread01(QThread):
    """
    to tell the server that the local database is updated successfully.
    the 'sku_ids' parameter in self.dict01 is new to tell the server the updated cv_id.
    """

    def __init__(self, parent=None, client_ip='127.0.0.1', logger_name='hobin', *, utm_medium='cashier',
                 utm_source='cmbox_cm002',sign_key='4b111cc14a33b88e37e2e2934f493458',
                 url_sku_dwonload_finished='https://api.lang.commaretail.com/cashier/cv_sync/sku_finish',
                 store_id='2', screen_id='5', system_version='windows', api_ver='1.0', device_id='cashier',
                 csp_id='cashier_0001', **kwargs):
        super().__init__(parent)
        # for http request
        self.url_sku_dwonload_finished = url_sku_dwonload_finished
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
                       'sku_ids': '',
                       'client_ip': client_ip}

        # some variables
        self.parent = parent
        self.mylogger_sku_download_finished01 = logging.getLogger(logger_name)
        self.headers01 = {'User-Agent': 'python-requests', 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate',
                          'Connection': 'close'}
        self.resp01 = None
        self.dict02 = {}  # the dictionary object of the first HTTP result
        self.mylogger_sku_download_finished01.info('The initialization of skuDownloadFinished thread is successful.')


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
        self.mylogger_sku_download_finished01.info('skuDownloadFinished thread begins')
        self.dict01['client_time'] = str(int(datetime.now().timestamp()))
        self.dict01['api_sign'] = self.api_sign_hexdigest(self.dict01)
        try:
            self.mylogger_sku_download_finished01.info('skuDownloadFinished thread: the header is %s and the data part is %s' % (self.headers01, self.dict01))
            self.resp01 = requests.post(self.url_sku_dwonload_finished, headers=self.headers01, data=self.dict01, timeout=8)
            self.mylogger_sku_download_finished01.info('The header information of first request is %s' %self.resp01.request.headers)
            self.mylogger_sku_download_finished01.info('The header information of first response is %s' % self.resp01.headers)
            if self.resp01.status_code == 200:
                self.dict02 = json.loads(self.resp01.text)
                self.mylogger_sku_download_finished01.info('skuDownloadFinished thread: the response of server is %s' %self.dict02)
                if self.dict02['code'] == 200:
                    self.mylogger_sku_download_finished01.info('skuDownloadFinished thread: the server receives the message.')
                else:
                    self.mylogger_sku_download_finished01.error('skuDownloadFinished thread: ---------the error of server logical part happens---------')
            else:
                self.mylogger_sku_download_finished01.error('skuDownloadFinished thread: ---------the status code of the response is not 200---------')

        except requests.exceptions.ReadTimeout:
            self.mylogger_sku_download_finished01.error('***------------------------Be careful! Error occurs in skuDownloadFinished thread!------------------------***',exc_info=True)

        except BaseException:
            self.mylogger_sku_download_finished01.error('***------------------------Be careful! Error occurs in skuDownloadFinished thread!------------------------***',exc_info=True)
        self.mylogger_sku_download_finished01.info('skuDownloadFinished thread ends')


if __name__ == '__main__':
    mylogging = MyLogging1(logger_name='hobin')
    #
    a = skuDownloadThread01()
    a.start()
    while a.isRunning():
        pass
    # pdb.set_trace()
    #
    # mylogging.logger.info('------------------------------------------------')
    # b = skuDownloadFinishedThread01()
    # b.dict01['sku_ids'] = '134,137'
    # b.start()
    # while b.isRunning():
    #     pass
    # pdb.set_trace()

