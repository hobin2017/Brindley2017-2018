"""
Reading a image and then post it to Baidu API indirectly
"""

import requests
import collections
import hashlib
# Test 1------------------------------------------------------------------------------------------------------
"""
access the API of Baidu indirectly!
"""
sign_key = "4b111cc14a33b88e37e2e2934f493458"

def api_sign_hexdigest(dict):
    # print('api_sign', dict, len(dict))

    api_sign = dict.get('api_sign')
    # print('api_sign', api_sign)

    ordered_dict = collections.OrderedDict(sorted(dict.items()))
    # print('ordered_dict', ordered_dict)

    input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
    # print('input', input)

    check_str = input + '&' + sign_key
    # print('check_str', check_str)

    hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
    # print('hexdigest', hexdigest)

    return hexdigest


dict01 = {"api_sign":"4b111cc14a33b88e37e2e2934f493458",
          'utm_medium':'app',
          'utm_source':'box',
          'store_id': '1',
          'client_time':'1516603324'}

url01 = 'http://api.commaai.xin/v1/face/find_user'


with open('.\\images\\linchao.jpg', 'rb') as f:
    binary_data = f.read()  # the length of this picture is 32639;
    files01 = {'face_photo':binary_data}
    print(files01)
    print(len(files01['face_photo']))
    dict02 = {'utm_medium':'app',
              'utm_source':'box',
              'store_id': 1,
              'client_time':'1516603324',
              'api_sign':api_sign_hexdigest(dict01)
              }
    resp01 = requests.post(url01, files=files01, data=dict02)
    print('--------------------------------------------------------------------')
    print(resp01.text)
# ------------------------------------------------------------------------------------------------------------


