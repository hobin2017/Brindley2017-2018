# -*- coding: utf-8 -*-
"""
local server for Klas Singtel
Normally, some changes are required when using this local server:
  1, the configuration file for computer, PayClient.sh, needs to contain the start of the local server;
  2, the configuration file for Klas, Klas2_Singtel.cfg, needs the destination host is 127.0.0.1;
  3, installing the flask third-party package in that computer;

author: hobin;
email = '627227669@qq.com';
"""
from datetime import datetime
import time
import json

from flask import Flask, request
app = Flask(__name__) # Flask constructor takes the name of current module (__name__) as argument.


@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/cashier/order/create', methods=['POST',])
def order_work01():
    print('---------------------------order_work01 starts---------------------------')
    print('the http header with type %s: \n%s' % (type(request.headers), request.headers))
    print('the html form data with type %s: %s' %(type(request.form), request.form))
    current_time = str(int(datetime.now().timestamp()))
    order_json_data = {"code":200,"msg":"生成订单成功","time":current_time,
                 "data":{"order_no":"SO201901140000000000",
                         "order_link":"https:\/\/sys-singtel.commaai.cn\/payment\/index\/index?order_no=%s" %current_time}
                 }
    print('---------------------------order_work01 ends---------------------------')
    return json.dumps(order_json_data)

@app.route('/cashier/face/find_user', methods=['POST',])
def account_work01():
    print('---------------------------account_work01 starts---------------------------')
    print('the http header with type %s: \n%s' % (type(request.headers), request.headers))
    print('the html form data with type %s: %s' % (type(request.form), request.form))
    print('the file with type %s: %s' %(type(request.files), request.files))
    current_time = str(int(datetime.now().timestamp()))
    time.sleep(1.5)
    account_json_data = {'data': {'real_name': None,
                                  'oss_return': {'path': 'face/search/201901/11/52e5ae03bbc4c0fc958d28fdbb454639924.jpg',
                                                 'visit_path': '127.0.0.1'},
                                  'user_id': 1,
                                  'nick_name': 'singtel',
                                  'wxpay_entrust': 1,
                                  'avatar_url': '',
                                  'identity_num': None},
                         'msg': '搜索成功', 'time': current_time, 'code': 200}
    print('---------------------------account_work01 ends---------------------------')
    return json.dumps(account_json_data)

@app.route('/cashier/order/prepaid', methods=['POST',])
def gesture_pay_work01():
    print('---------------------------gesture_pay_work01 starts---------------------------')
    print('the http header with type %s: \n%s' % (type(request.headers), request.headers))
    print('the html form data with type %s: %s' % (type(request.form), request.form))
    current_time = str(int(datetime.now().timestamp()))
    gesture_pay_json_data = {'data': {'not_paying_money': 0,
                                      'wap_pay': {'alipay': None, 'wxpay': None},
                                      'order_info': {'order_weight': 0, 'flag_test': 0, 'create_time': 0,
                                                     'flag_delete': 0, 'order_discount': 0, 'order_id': 0,
                                                     'order_amount': '1.25', 'pay_model': 0, 'checkstand': 1,
                                                     'coupon_id': 0, 'utm_medium': 'cashier', 'update_time': 0,
                                                     'user_id': 0, 'partner_id': 1, 'order_type': 2, 'refund_status': 0,
                                                     'remark': None, 'flag_rollback': 0, 'delete_time': 0,
                                                     'order_promote': '1.25', 'pay_time': 0, 'order_no': 'SO201901140000000000',
                                                     'limit_amount': '1.25', 'utm_source': 'cmbox_1', 'refund_time': 0,
                                                     'store_id': 1, 'screen_id': 7, 'order_status': 1},
                                      'payment_details': [],
                                      'order_pay_status': 0,
                                      'wxmch_entrust': {}},
                             'msg': 'success',
                             'time': current_time,
                             'code': 200}
    print('---------------------------gesture_pay_work01 ends---------------------------')
    return json.dumps(gesture_pay_json_data)

@app.route('/cashier/order/attach_upload', methods=['POST',])
def image_upload_work01():
    print('---------------------------image_upload_work01 starts---------------------------')
    print('the http header with type %s: \n%s' % (type(request.headers), request.headers))
    print('the html form data with type %s: %s' % (type(request.form), request.form))
    print('the file with type %s: %s' % (type(request.files), request.files))
    current_time = str(int(datetime.now().timestamp()))
    image_upload_json_data = {'data': {'attach_id': '1111'},
                              'msg': '上传成功',
                              'time': current_time,
                              'code': 200}
    print('---------------------------image_upload_work01 ends---------------------------')
    return json.dumps(image_upload_json_data)

@app.route('/order/attach/upload_goods_qrcode', methods=['POST',])
def item_quality_work01():
    return ''

@app.route('/cashier/cv_sync/sku_dwonload', methods=['POST',])
def skuDownloadThread_work01():
    return ''

@app.route('/cashier/cv_sync/sku_finish', methods=['POST',])
def skuDownloadFinishedThread_work01():
    return ''

if __name__ =='__main__':
    # debug: If the application should be restarted manually for each change in the code.
    # To avoid this inconvenience, enable debug support. The server will then reload itself if the code changes.
    # options: To be forwarded to underlying Werkzeug server.
    app.run(host='127.0.0.1', port=80, debug=True)  # app.run(host, port, debug, options)

