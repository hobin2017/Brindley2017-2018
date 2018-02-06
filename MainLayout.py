"""
Layout management and definition of function
author = hobin
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel

from ShoppingList import ShoppingList
from CameraLayout import CameraWidget2

class MainLayout(QWidget):
    """
    The payment page for the payment system
    """
    def __init__(self, parent=None):
        super(MainLayout, self).__init__(parent)
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
        self.mainlayout.rightlayout.firstlayout.imgDefault = QPixmap()
        self.mainlayout.rightlayout.firstlayout.imgDefault.load('.\\Images\\DeafaultPortrait.jpg')
        self.mainlayout.rightlayout.firstlayout.imgDefault.setDevicePixelRatio(2)
        self.mainlayout.rightlayout.firstlayout.imgUser = QPixmap()  # It will be used to load the binary data given by the Account thread
        self.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(self.mainlayout.rightlayout.firstlayout.imgDefault)
        self.mainlayout.rightlayout.firstlayout.userName = QLabel()
        self.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.mainlayout.rightlayout.firstlayout.addWidget(self.mainlayout.rightlayout.firstlayout.userPortrait)
        self.mainlayout.rightlayout.firstlayout.addWidget(self.mainlayout.rightlayout.firstlayout.userName)
        self.mainlayout.rightlayout.addLayout(self.mainlayout.rightlayout.firstlayout, 1) # the second parameter is stretch factor
        # 2.2 second layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.secondlayout = CameraWidget2()
        self.mainlayout.rightlayout.addWidget(self.mainlayout.rightlayout.secondlayout, 4) # the second parameter is stretch factor
        # 2.3 third layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.thirdlayout = QLabel()
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
        self.mainlayout.leftlayout.firstlayout.label2.setText(str(sum))

