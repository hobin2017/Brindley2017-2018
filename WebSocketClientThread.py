"""
WebSocket Client
"""

import sys
from PyQt5 import QtWebSockets
from socketIO_client import SocketIO
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QUrl, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow
import logging



class MyThread8(QThread):
    """
    WebSocket client
    It sends data to my server to indicate that the machine is alive;
    It receives the data from my server to open door;
    It receives the data from my server to confirm that the order is paid by QR code or gesture method;
    """
    payclear_success = pyqtSignal()
    payclear_failure = pyqtSignal()
    opendoor = pyqtSignal(object)
    
    def __init__(self, socketUrl='http://sys.commaai.cn', storeName='development center for testing', storeId='2', screenId='1'):
        super(MyThread8, self).__init__()
        self.socketUrl = socketUrl
        self.storeName = storeName
        self.storeId = storeId
        self.screenId = screenId
        self.socket = SocketIO(socketUrl, port=60000)
        self.socket.on('reconnect', self.on_reconnect)
        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        self.socket.on('msg', self.on_msg_response)  # for listen
        self.msg = '{"store_id":"%s", "remark":"%s", "screen_id": "%s"}'%(storeId, storeName, screenId)
        print('Initialization of WebSocket thread is successful.')


    def on_connect(self):
        print('WebSocket-Client thread connects')


    def on_disconnect(self):
        """I guess the error information comes from the LoggingNamespace."""
        print('WebSocket-Client thread disconnects')


    def on_reconnect(self):
        print('WebSocket-Client thread reconnects')


    def on_msg_response(self,*args):
        """
        Getting the response from the server;
        input parameter 'args': it is tuple type;
        If the information is related to the payment, the first element is a dictionary.
          If using qrcode to buy the products, the result may look like this:
           ({'token': 'a45726618c1b60f794e6120877a5292b03edeeb1', 'store_id': '2', 'action': 'payclear', 'order_no': 'SO201802071734584166', 'pay_type': '1', 'user_id': '3503', 'rfid_list': '', 'screen_id': '1', 'door_id': '1', 'code': '1', 'msg': 'success'},)
          If using gesture to buy the products, the result may look like this:
           ({'token': 'a45726618c1b60f794e6120877a5292b03edeeb1', 'store_id': '2', 'action': 'payclear', 'order_no': 'SO201802071740584193', 'pay_type': '1', 'user_id': '3503', 'rfid_list': '', 'screen_id': '1', 'door_id': '1', 'code': '1', 'msg': 'success'},)
        If the information is related to the door, the first element is a dictionary.
          If using face recognition to open door is failed, there will be not result.
          If using face recognition to open door is successful, the result may look like this:
           ({'token': '52ca8bc2253529843378def2972249da3b934349', 'store_id': '2', 'action': 'opendoor', 'door_id': '1', 'user_id': '336', 'type': 'face', 'code': '1', 'msg': 'success'},)
          If using qrcode to open door, the result may look like this:
           ({'token': '52ca8bc2253529843378def2972249da3b934349', 'store_id': '2', 'action': 'opendoor', 'user_id': '', 'type': 'qrcode', 'open_id': '', 'door_id': '1', 'code': '1', 'msg': 'success'},)

        """
        print('WebSocket-Client thread gets:', args)
        if args[0]['action'] == 'opendoor':
            self.detect_opendoor.emit(args[0]['door_id'])
        elif args[0]['action'] == 'payclear' and args[0]['code']== '1':
            self.payclear_success.emit()
        elif args[0]['action'] == 'payclear' and args[0]['code']== '0':
            self.payclear_failure.emit()


    def run(self):
        try:
            self.socket.emit('join', self.storeId)
            self.socket.wait()  # wait forever
        except Exception as e:
            print(e)
            print('---------------------Error happens in the run funciton of WebSocket Thread-------------------------')


    def ping_timer(self):
        """It is like heart-beating."""
        try:
            print('WebSocket-Client thread sends:', self.msg)
            self.socket.emit('ping server', self.msg)
        except Exception as e:
            print(e)
            print('--------------Error happens in the ping_timer function of WebSocket Thread-------------------------')


class MyThread8_1(QThread):
    """
    WebSocket client
    It sends data to my server to indicate that the machine is alive;
    It receives the data from my server to open door;
    It receives the data from my server to confirm that the order is paid by QR code or gesture method;
    Compared with the MyThread8 class, the logging module is introduced to this module at first time.
    """
    payclear_success = pyqtSignal()
    payclear_failure = pyqtSignal()
    opendoor = pyqtSignal(object)

    def __init__(self, logger_name='hobin', *, socketUrl='http://sys.commaai.cn', socketPort=60000, storeName='development center for testing',
                 storeId='2', screenId='1',  **kwargs):
        super(MyThread8_1, self).__init__()
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.socketUrl = socketUrl
        self.storeName = storeName
        self.storeId = storeId
        self.screenId = screenId
        self.socket = SocketIO(socketUrl, port=socketPort)
        self.socket.on('reconnect', self.on_reconnect)
        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        self.socket.on('msg', self.on_msg_response)  # for listen

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.socketUrl = kwargs['socketUrl']
        # self.storeName = kwargs['storeName']
        # self.storeId = kwargs['storeId']
        # self.screenId = kwargs['screenId']
        # self.socket = SocketIO(kwargs['socketUrl'], port=kwargs['socketPort'])
        # self.socket.on('reconnect', self.on_reconnect)
        # self.socket.on('connect', self.on_connect)
        # self.socket.on('disconnect', self.on_disconnect)
        # self.socket.on('msg', self.on_msg_response)  # for listen

        # some variables
        self.mylogger8_1 = logging.getLogger(logger_name)
        self.msg = '{"store_id":"%s", "remark":"%s", "screen_id": "%s"}' % (self.storeId, self.storeName, self.screenId)
        # print('Initialization of WebSocket thread is successful.')
        self.mylogger8_1.info('Initialization of WebSocket thread is successful.')

    def on_connect(self):
        # print('WebSocket-Client thread connects')
        self.mylogger8_1.info('WebSocket-Client thread connects')

    def on_disconnect(self):
        """I guess the error information comes from the LoggingNamespace."""
        # print('WebSocket-Client thread disconnects')
        self.mylogger8_1.info('WebSocket-Client thread disconnects')

    def on_reconnect(self):
        print('WebSocket-Client thread reconnects')
        self.mylogger8_1.info('WebSocket-Client thread reconnects')

    def on_msg_response(self, *args):
        """
        Getting the response from the server;
        input parameter 'args': it is tuple type;
        If the information is related to the payment, the first element is a dictionary.
          If using qrcode to buy the products, the result may look like this:
           ({'token': 'a45726618c1b60f794e6120877a5292b03edeeb1', 'store_id': '2', 'action': 'payclear', 'order_no': 'SO201802071734584166', 'pay_type': '1', 'user_id': '3503', 'rfid_list': '', 'screen_id': '1', 'door_id': '1', 'code': '1', 'msg': 'success'},)
          If using gesture to buy the products, the result may look like this:
           ({'token': 'a45726618c1b60f794e6120877a5292b03edeeb1', 'store_id': '2', 'action': 'payclear', 'order_no': 'SO201802071740584193', 'pay_type': '1', 'user_id': '3503', 'rfid_list': '', 'screen_id': '1', 'door_id': '1', 'code': '1', 'msg': 'success'},)
        If the information is related to the door, the first element is a dictionary.
          If using face recognition to open door is failed, there will be not result.
          If using face recognition to open door is successful, the result may look like this:
           ({'token': '52ca8bc2253529843378def2972249da3b934349', 'store_id': '2', 'action': 'opendoor', 'door_id': '1', 'user_id': '336', 'type': 'face', 'code': '1', 'msg': 'success'},)
          If using qrcode to open door, the result may look like this:
           ({'token': '52ca8bc2253529843378def2972249da3b934349', 'store_id': '2', 'action': 'opendoor', 'user_id': '', 'type': 'qrcode', 'open_id': '', 'door_id': '1', 'code': '1', 'msg': 'success'},)

        """
        # print('WebSocket-Client thread gets:', args)
        self.mylogger8_1.info('WebSocket-Client thread gets: %s' % args)
        if args[0]['action'] == 'opendoor':
            self.detect_opendoor.emit(args[0]['door_id'])
        elif args[0]['action'] == 'payclear' and args[0]['code'] == '1':
            self.payclear_success.emit()
        elif args[0]['action'] == 'payclear' and args[0]['code'] == '0':
            self.payclear_failure.emit()

    def run(self):
        try:
            self.socket.emit('join', self.storeId)
            self.socket.wait()  # wait forever
        except Exception as e:
            # print(e)
            self.mylogger8_1.error(e)
            # print('---------------------Error happens in the run funciton of WebSocket Thread-------------------------')
            self.mylogger8_1.error('---------------------Error happens in the run funciton of WebSocket Thread-------------------------')

    def ping_timer(self):
        """It is like heart-beating."""
        try:
            # print('WebSocket-Client thread sends:', self.msg)
            self.mylogger8_1.info('WebSocket-Client thread sends: %s' % self.msg)
            self.socket.emit('ping server', self.msg)
        except Exception as e:
            # print(e)
            self.mylogger8_1.error(e)
            # print('--------------Error happens in the ping_timer function of WebSocket Thread-------------------------')
            self.mylogger8_1.error('--------------Error happens in the ping_timer function of WebSocket Thread-------------------------')


class MyThread8_2(QObject):
    """
    Using the QWebSocket class (Not implemented yet);
    It sends data to my server to indicate that the machine is alive;
    It receives the data from my server to open door;
    It receives the data from my server to confirm that the order is paid by QR code or gesture method;
    """
    payclear_success = pyqtSignal()
    payclear_failure = pyqtSignal()
    opendoor = pyqtSignal(object)

    def __init__(self, socketUrl='http://sys.commaai.cn', storeName='development center for testing',
                 socketUrl_port=60000, storeId=2,screenId=1):
        super(MyThread8_2, self).__init__()
        self.socketUrl = socketUrl
        self.socketUrl_port = socketUrl_port
        self.storeName = storeName
        self.storeId = storeId
        self.screenId = screenId
        self.msg = '{"store_id":"%s", "remark":"%s", "screen_id": "%s"}' % (storeId, storeName, screenId)
        # print(self.msg)
        self.socket_client = QtWebSockets.QWebSocket('', QtWebSockets.QWebSocketProtocol.Version13, self)
        self.socket_client.connected.connect(self.on_connect)
        self.socket_client.disconnected.connect(self.on_disconnect)
        self.socket_client.textMessageReceived.connect(self.on_msg_response)
        self.socket_client.pong.connect(self.onPong)
        self.socket_client.open(QUrl('%s:%s' % (self.socketUrl, self.socketUrl_port)))  # Not success

        self.timer = QTimer()
        self.timer.timeout.connect(self.ping_timer)
        self.timer.start(3000)

    def onPong(self, elapsedTime, payload):
        print("onPong - time: {} ; payload: {}".format(elapsedTime, payload))

    def on_connect(self):
        print('WebSocket-Client connects')

    def on_disconnect(self):
        """I guess the error information comes from the LoggingNamespace."""
        print('WebSocket-Client  disconnects')


    def on_msg_response(self, args):
        """
        Getting the response from the server;
        input parameter 'args': it is tuple type;
        If the information is related to the payment, the first element is a dictionary.
          If using qrcode to buy the products, the result may look like this:
           ({'token': 'a45726618c1b60f794e6120877a5292b03edeeb1', 'store_id': '2', 'action': 'payclear', 'order_no': 'SO201802071734584166', 'pay_type': '1', 'user_id': '3503', 'rfid_list': '', 'screen_id': '1', 'door_id': '1', 'code': '1', 'msg': 'success'},)
          If using gesture to buy the products, the result may look like this:
           ({'token': 'a45726618c1b60f794e6120877a5292b03edeeb1', 'store_id': '2', 'action': 'payclear', 'order_no': 'SO201802071740584193', 'pay_type': '1', 'user_id': '3503', 'rfid_list': '', 'screen_id': '1', 'door_id': '1', 'code': '1', 'msg': 'success'},)
        If the information is related to the door, the first element is a dictionary.
          If using face recognition to open door is failed, there will be not result.
          If using face recognition to open door is successful, the result may look like this:
           ({'token': '52ca8bc2253529843378def2972249da3b934349', 'store_id': '2', 'action': 'opendoor', 'door_id': '1', 'user_id': '336', 'type': 'face', 'code': '1', 'msg': 'success'},)
          If using qrcode to open door, the result may look like this:
           ({'token': '52ca8bc2253529843378def2972249da3b934349', 'store_id': '2', 'action': 'opendoor', 'user_id': '', 'type': 'qrcode', 'open_id': '', 'door_id': '1', 'code': '1', 'msg': 'success'},)

        """
        print('Type of the message is: %s' %type(args))
        print('WebSocket-Client gets:', args)
        # if args[0]['action'] == 'opendoor':
        #     self.detect_opendoor.emit(args[0]['door_id'])
        # elif args[0]['action'] == 'payclear' and args[0]['code'] == '1':
        #     self.payclear_success.emit()
        # elif args[0]['action'] == 'payclear' and args[0]['code'] == '0':
        #     self.payclear_failure.emit()


    def ping_timer(self):
        """It is like heart-beating."""
        try:
            print('WebSocket-Client sends:', self.msg)
        except Exception as e:
            print(e)
            print('--------------Error happens in the ping_timer function of WebSocket Thread-------------------------')


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.thread = MyThread8()
        self.timer = QTimer()
        self.timer.timeout.connect(self.thread.ping_timer)
        self.timer.start(60000)
        self.thread.start()

        # self.setCentralWidget()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # mywindow = MainWindow()
    # mywindow.show()
    mythread = MyThread8()
    sys.exit(app.exec_())

