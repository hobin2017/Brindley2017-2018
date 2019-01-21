# -*- coding: utf-8 -*-
"""
setStyleSheet('border: 1px solid black') or setStyleSheet('border: 1px dotted black') can show the border of rectangle.
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame, QVBoxLayout, QHBoxLayout


class PaySuccessLayout(QFrame):

    def __init__(self, *, font_family01='萍方-简', **kwargs):
        super().__init__()
        print('font_family01 of PaySuccessLayout is %s' % font_family01)
        self.setStyleSheet('''
            background: white;
            ''')
        # the first way
        # self.pic_pixmap99 = QPixmap()
        # self.pic_pixmap99.load('./Images/success_payment01.png')
        # self.pic_widget99 = QLabel(self)
        # self.pic_widget99.setScaledContents(True)
        # self.pic_widget99.setPixmap(self.pic_pixmap99)
        # self.pic_widget99.move(85, 400)

        # the second way
        #
        self.logo_pixmap = QPixmap()
        self.logo_pixmap.load('./Images/logo.png')
        self.logo_widget = QLabel(self)
        self.logo_widget.setScaledContents(True)
        self.logo_widget.setFixedSize(100, 100)
        self.logo_widget.setPixmap(self.logo_pixmap)

        #
        self.pic_pixmap = QPixmap()
        self.pic_pixmap.load('./Images/ok.png')
        self.pic_widget = QLabel(self)
        self.pic_widget.setScaledContents(True)
        self.pic_widget.setFixedSize(68, 68)
        self.pic_widget.setPixmap(self.pic_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setStyleSheet('font-size: 36px')
        self.title_widget.setFont(QFont(font_family01))
        self.title_widget.setAlignment(Qt.AlignCenter)
        self.title_widget.setText('Payment completed')

        #
        self.shopping_reminder = QLabel(self)
        self.shopping_reminder.setStyleSheet('color: #888888;font-size:20px;')
        self.shopping_reminder.setFont(QFont(font_family01))
        self.shopping_reminder.setAlignment(Qt.AlignCenter)
        self.shopping_reminder.setText('For demonstration only')

        # layout management
        self.logo_widget.move(220, 420)
        self.pic_widget.move(70, 555)
        self.title_widget.move(150, 547)
        self.shopping_reminder.move(150, 600)


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        # adding special font
        singtel_font_database = QFontDatabase()
        singtel_font_database.addApplicationFont(r".\font\PingFang-SC.ttf")  # 萍方-简
        singtel_font_database.addApplicationFont(r".\font\WeChatSansSS-Medium.ttf")  # WeChat Sans SS Medium
        assert QFont.exactMatch(QFont('萍方-简'))  # to check whether the font can be used.
        assert QFont.exactMatch(QFont('WeChat Sans SS Medium'))  # to check whether the font can be used.
        # print(singtel_font_database.families())  # printing all supported font
        print('-----------------------adding special font successfully------------------------------------------')
        self.main_widget = PaySuccessLayout()
        self.main_widget.setFixedSize(540, 1080)
        self.setCentralWidget(self.main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    sys.exit(app.exec_())
