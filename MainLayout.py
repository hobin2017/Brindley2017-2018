"""
Layout management and definition of function
author = hobin
"""
import sys

import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QStackedLayout, QGridLayout, QMainWindow, \
    QApplication

from ShoppingList import ShoppingList
from CameraLayout import CameraWidget2_2


class MainLayout(QWidget):
    """
    The payment page for the payment system
    The configuration is given by the keyword argument 'kwargs'.
    """
    def __init__(self, parent=None, **kwargs):
        super(MainLayout, self).__init__(parent)
        # all file path configuration
        dir_path = os.path.dirname(__file__)
        image_path = os.path.join(dir_path, 'Images')
        deafaultPortrait_path = os.path.join(image_path, 'DeafaultPortrait.jpg')
        noAuthorization_path = os.path.join(image_path, 'NoAuthorization.png')

        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        self.mainlayout.leftlayout = QVBoxLayout()
        self.mainlayout.rightlayout = QVBoxLayout()
        self.mainlayout.addLayout(self.mainlayout.leftlayout, 6)# the second parameter is stretch factor
        self.mainlayout.addLayout(self.mainlayout.rightlayout, 1)# the second parameter is stretch factor
        # 1 Layout Management for 'self.mainlayout.leftlayout'
        # 1.1 first layout in 'self.mainlayout.leftlayout'
        self.mainlayout.leftlayout.firstlayout = QHBoxLayout()
        self.mainlayout.leftlayout.firstlayout.label1 = QLabel()
        self.mainlayout.leftlayout.firstlayout.label1.setText('购物车')
        self.mainlayout.leftlayout.firstlayout.label1.setAlignment(Qt.AlignLeft)
        self.mainlayout.leftlayout.firstlayout.label1.setMargin(20)
        self.mainlayout.leftlayout.firstlayout.label1.setFont(QFont('宋体', 60, 100))
        self.mainlayout.leftlayout.firstlayout.label2 = QLabel()
        self.mainlayout.leftlayout.firstlayout.label2.setText('0.0')
        self.mainlayout.leftlayout.firstlayout.label2.setFont(QFont('宋体', 60, 100))
        self.mainlayout.leftlayout.firstlayout.label2.setAlignment(Qt.AlignRight)
        self.mainlayout.leftlayout.firstlayout.label2.setMargin(20)
        self.mainlayout.leftlayout.firstlayout.addWidget(self.mainlayout.leftlayout.firstlayout.label1)
        self.mainlayout.leftlayout.firstlayout.addWidget(self.mainlayout.leftlayout.firstlayout.label2)
        self.mainlayout.leftlayout.addLayout(self.mainlayout.leftlayout.firstlayout, 1)# the second parameter is stretch factor
        # 1.2 second layout in 'self.mainlayout.leftlayout'
        self.mainlayout.leftlayout.secondlayout = ShoppingList()
        self.mainlayout.leftlayout.addWidget(self.mainlayout.leftlayout.secondlayout, 5)# the second parameter is stretch factor
        # 2 Layout Management for 'self.mainlayout.rightlayout'
        # 2.1 first layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.firstlayout = QHBoxLayout()
        self.mainlayout.rightlayout.firstlayout.userPortrait = QLabel()
        self.mainlayout.rightlayout.firstlayout.userPortrait.setScaledContents(True)
        self.mainlayout.rightlayout.firstlayout.userPortrait.setFixedSize(80, 80)
        self.mainlayout.rightlayout.firstlayout.imgDefault = QPixmap()
        self.mainlayout.rightlayout.firstlayout.imgDefault.load(deafaultPortrait_path)
        self.mainlayout.rightlayout.firstlayout.imgDefault.setDevicePixelRatio(2)
        self.mainlayout.rightlayout.firstlayout.imgUser = QPixmap()  # It will be used to load the binary data given by the Account thread
        self.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(self.mainlayout.rightlayout.firstlayout.imgDefault)
        self.mainlayout.rightlayout.firstlayout.userName = QLabel()
        self.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.mainlayout.rightlayout.firstlayout.userName.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.mainlayout.rightlayout.firstlayout.addWidget(self.mainlayout.rightlayout.firstlayout.userPortrait)
        self.mainlayout.rightlayout.firstlayout.addWidget(self.mainlayout.rightlayout.firstlayout.userName)
        self.mainlayout.rightlayout.addLayout(self.mainlayout.rightlayout.firstlayout, 1) # the second parameter is stretch factor
        # 2.2 second layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.secondlayout_main = QStackedLayout()
        self.mainlayout.rightlayout.secondlayout = CameraWidget2_2(**kwargs)
        self.mainlayout.rightlayout.secondlayout_2ndWidget = QLabel()
        self.mainlayout.rightlayout.secondlayout_2ndWidget.setScaledContents(True)
        self.mainlayout.rightlayout.secondlayout_2ndWidget.setFixedSize(600, 450)
        self.mainlayout.rightlayout.secondlayout_2ndWidget.setAlignment(Qt.AlignCenter)
        self.mainlayout.rightlayout.secondlayout_2ndWidget.img = QPixmap()
        self.mainlayout.rightlayout.secondlayout_2ndWidget.img.load(noAuthorization_path)
        self.mainlayout.rightlayout.secondlayout_2ndWidget.setPixmap(self.mainlayout.rightlayout.secondlayout_2ndWidget.img)
        self.mainlayout.rightlayout.secondlayout_main.addWidget(self.mainlayout.rightlayout.secondlayout)
        self.mainlayout.rightlayout.secondlayout_main.addWidget(self.mainlayout.rightlayout.secondlayout_2ndWidget)
        self.mainlayout.rightlayout.addLayout(self.mainlayout.rightlayout.secondlayout_main, 4) # the second parameter is stretch factor
        # 2.3 third layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.thirdlayout = QLabel()
        self.mainlayout.rightlayout.thirdlayout.setAlignment(Qt.AlignCenter)
        self.mainlayout.rightlayout.img_qrcode = QPixmap()
        self.mainlayout.rightlayout.addWidget(self.mainlayout.rightlayout.thirdlayout, 2) # the second parameter is stretch factor


    def renewSum(self, mylist):
        """
        renew the total amount of products
        :param mylist: its element containing three components: str, str, str
        :return: void
        """
        sum = 0.0
        for product in mylist:
            sum = sum + float(product[2])
        self.mainlayout.leftlayout.firstlayout.label2.setText('%.2f' % sum)


class MainLayout_1(QWidget):

    def __init__(self, parent=None):
        super(MainLayout_1, self).__init__(parent)
        self.mainlayout = QGridLayout()
        self.mainlayout.setSpacing(0)
        self.setLayout(self.mainlayout)
        self.left_firstlayout = QHBoxLayout()
        self.right_firstitem = QLabel()
        self.right_firstitem.setStyleSheet('QLabel {background-color: green}')
        self.left_seconditem = ShoppingList()
        self.right_seconditem = QLabel()
        self.right_seconditem.setStyleSheet('QLabel {background-color: green}')
        self.mainlayout.addLayout(self.left_firstlayout, 0, 0, 1, 7)
        self.mainlayout.addWidget(self.left_seconditem, 1, 0, 1, 7)
        self.mainlayout.addWidget(self.right_firstitem, 0, 7, 1, 2)
        self.mainlayout.addWidget(self.right_seconditem, 1, 7, 1, 2)

        # 1
        self.lf_title = QLabel()
        self.lf_title.setAlignment(Qt.AlignLeft)
        self.lf_title.setText('购物车')
        self.lf_price = QLabel()
        self.lf_price.setAlignment(Qt.AlignRight)
        self.lf_price.setText('0.0')
        self.left_firstlayout.addWidget(self.lf_title)
        self.left_firstlayout.addWidget(self.lf_price)

        # 2
        self.right_firstlayout = QHBoxLayout()
        self.right_firstitem.setLayout(self.right_firstlayout)
        self.rf_userImg = QLabel()
        self.rf_userImg.setScaledContents(True)
        self.rf_userName = QLabel()
        self.rf_userName.setAlignment(Qt.AlignLeft)
        self.rf_userName.setText('未能识别会员信息')
        self.right_firstlayout.addWidget(self.rf_userImg)
        self.right_firstlayout.addWidget(self.rf_userName)

        # 3
        self.right_secondlayout = QVBoxLayout()
        self.right_seconditem.setLayout(self.right_secondlayout)
        self.rs_firstlayout = QStackedLayout()
        self.rs_text = QLabel()
        self.rs_text.setText('刷脸设置+开通免密=支持手势支付')
        self.rs_qrcode = QLabel()
        self.right_secondlayout.addLayout(self.rs_firstlayout)
        self.right_secondlayout.addWidget(self.rs_text)
        self.right_secondlayout.addWidget(self.rs_qrcode)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_widget = MainLayout_1()
        self.setCentralWidget(self.main_widget)


if __name__ == '__main__':
    global mywindow
    try:
        app = QApplication(sys.argv)
        mywindow = MainWindow()
        mywindow.show()
        sys.exit(app.exec_())
    except BaseException as e:
        print(e)

