"""
doing the http request with the urllib package;
using logging rather than print statement;
"""
import logging
from urllib import request
import json
import sys

# -----------------------------------------------logging------------------------------------------------------------
# one logger can use more than one handler and filter;
# one handler can use more than one filter;
logger1 = logging.getLogger('HOBIN')
logger1.setLevel(logging.DEBUG) # level: DEBUG < INFO < WARNING < ERROR < CRITICAL
# the level needs to be specified before using. the default level is WARNING.
handler1 = logging.StreamHandler(sys.stdout) # sys.stdout represents the screen.
# handler1.setLevel(logging.DEBUG)
formatter1 = logging.Formatter('%(asctime)s %(levelname)s in line%(lineno)s: %(name)s: %(message)s')
handler1.setFormatter(formatter1)
logger1.addHandler(handler1) # This indicates that the info of logger1 will be shown in the screen;
# filter1 = logging.Filter('HOBIN')
# logger1.addFilter(filter1) # filtering the information by the name of logger and can be used for handler as well
# -----------------------------------------------logging------------------------------------------------------------

req = request.Request('http://127.0.0.1:5000/test1/')
with request.urlopen(req) as f:
    data1 = f.read().decode('utf-8') # converting those bytes data to the string;
    data2 = json.loads(data1) # analysing the json data;

# -----------------------------------------------logging------------------------------------------------------------
# you can change the level of specific logger to a higher level, and then their debug information will not be shown.
# you can also change the level of specific StreamHandler to a higher level.
# you can use a new logger to record the info of a new section..
logger1.debug(type(data1)) # the data type is str.
logger1.debug(data1)
logger1.debug('--------------------------------------------------------------------------------------------')
logger1.debug(type(data2)) # the data type is dict.
logger1.debug(data2)
logger1.debug('--------------------------------------------------------------------------------------------')
logger1.debug(type(data2['employees']))
logger1.debug(data2['employees'])
logger1.debug('--------------------------------------------------------------------------------------------')
logger1.debug(type(data2['employees'][0]))
logger1.debug(data2['employees'][0])
# -----------------------------------------------logging------------------------------------------------------------







