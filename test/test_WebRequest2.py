"""
doing the http request with the requests package
"""
import logging
import sys
import requests
# -----------------------------------------------logging------------------------------------------------------------
logger1 = logging.getLogger('HOBIN')
logger1.setLevel(logging.DEBUG)
handler1 = logging.StreamHandler(sys.stdout)
formatter1 = logging.Formatter('%(levelname)s in line%(lineno)s: %(name)s: %(message)s')
handler1.setFormatter(formatter1)
logger1.addHandler(handler1)
# ------------------------------------------------------------------------------------------------------------------

r = requests.get('http://127.0.0.1:5000/test1/')  # GET method
logger1.debug(r.url)
logger1.debug(r.status_code)
logger1.debug(r.headers['content-type'])
logger1.debug(r.encoding)
logger1.debug(r.text)  # the data type of r.text is str.
logger1.debug(r.json())  # the data type of r.json is dict.
logger1.debug(r.json()['employees'][0])




