"""
WebSocket Client
"""

import sys
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from socketIO_client import SocketIO
# import logging
# logging.getLogger('requests').setLevel(logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)


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
    
    def __init__(self, socketUrl='http://sys.commaai.cn', storeName='development center for testing', storeId=2, screenId=1):
        super(MyThread8, self).__init__()
        self.socketUrl = socketUrl
        self.storeName = storeName
        self.storeId = storeId
        self.screenId = screenId
        self.socket = SocketIO(socketUrl,60000)
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
            self.socket.emit('WebSocket-Client thread ping server', self.msg)
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
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

