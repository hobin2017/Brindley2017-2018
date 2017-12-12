"""
Layout management and definition of function
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from ShoppingList import ShoppingList

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
        self.mainlayout.addLayout(self.mainlayout.leftlayout)
        self.mainlayout.addLayout(self.mainlayout.rightlayout)
        self.mainlayout.setStretchFactor(self.mainlayout.leftlayout, 5)
        self.mainlayout.setStretchFactor(self.mainlayout.rightlayout, 1)
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
        self.mainlayout.leftlayout.addLayout(self.mainlayout.leftlayout.firstlayout)
        self.mainlayout.leftlayout.setStretchFactor(self.mainlayout.leftlayout.firstlayout, 1)
        # 1.2 second layout in 'self.mainlayout.leftlayout'
        self.mainlayout.leftlayout.secondlayout = ShoppingList()
        self.mainlayout.leftlayout.addWidget(self.mainlayout.leftlayout.secondlayout)
        self.mainlayout.leftlayout.setStretchFactor(self.mainlayout.leftlayout.secondlayout, 5)
        # 2 Layout Management for 'self.mainlayout.rightlayout'
        # 2.1 first layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.firstlayout = QHBoxLayout()
        self.mainlayout.rightlayout.firstlayout.userPortrait = QLabel()
        self.mainlayout.rightlayout.firstlayout.img = QPixmap()
        self.mainlayout.rightlayout.firstlayout.img.load('.\\DeafaultPortrait.jpg')
        self.mainlayout.rightlayout.firstlayout.img.setDevicePixelRatio(2)
        self.mainlayout.rightlayout.firstlayout.userPortrait.setPixmap(self.mainlayout.rightlayout.firstlayout.img)
        self.mainlayout.rightlayout.firstlayout.userName = QLabel()
        self.mainlayout.rightlayout.firstlayout.userName.setText('Name')
        self.mainlayout.rightlayout.firstlayout.addWidget(self.mainlayout.rightlayout.firstlayout.userPortrait)
        self.mainlayout.rightlayout.firstlayout.addWidget(self.mainlayout.rightlayout.firstlayout.userName)
        self.mainlayout.rightlayout.addLayout(self.mainlayout.rightlayout.firstlayout)
        self.mainlayout.rightlayout.setStretchFactor(self.mainlayout.rightlayout.firstlayout, 1)
        # 2.2 second layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.secondlayout = QOpenGLWidget()
        self.mainlayout.rightlayout.addWidget(self.mainlayout.rightlayout.secondlayout)
        self.mainlayout.rightlayout.setStretchFactor(self.mainlayout.rightlayout.secondlayout, 3)
        # 2.3 third layout in 'self.mainlayout.rightlayout'
        self.mainlayout.rightlayout.thirdlayout = QLabel()
        self.mainlayout.rightlayout.addWidget(self.mainlayout.rightlayout.thirdlayout)
        self.mainlayout.rightlayout.setStretchFactor(self.mainlayout.rightlayout.thirdlayout, 2)

    def renewSum(self, mylist):
        """
        renew the total amount of products
        :param mylist: its element containing three components: str, str, float
        :return: void
        """
        sum = 0
        for product in mylist:
            sum = sum + product[2]
        self.mainlayout.leftlayout.firstlayout.label2.setText(str(sum))

