# -*- coding: utf-8 -*-
"""
setStyleSheet('border: 1px solid black') or setStyleSheet('border: 1px dotted black') can show the border of rectangle.
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame


class Singtel_StandbyLayout(QFrame):

    def __init__(self, parent=None, *, font_family01='萍方-简', **kwargs):
        super().__init__(parent)
        print('font_family01 of Singtel_StandbyLayout is %s' %font_family01)
        #
        self.setStyleSheet('''
            background: white;
            ''')
        # the widget is used for the text 'Please put your items within the identification zone'
        self.reminder01 = QLabel(self)
        self.reminder01.setFixedSize(969, 224)
        self.reminder01.setAlignment(Qt.AlignHCenter)
        self.reminder01.setFont(QFont(font_family01))
        self.reminder01.setText('''
            <p>Please put items </p>
            <p>within identification zone<p>
                    ''')
        self.reminder01.setStyleSheet('''
            color: #212121;
            font-size: 80px;
            ''')


        # the widget is used for the picture
        self.jpg_image = QPixmap()
        self.jpg_image.load('./Images/shape.png')
        self.pic_widget = QLabel(self)
        self.pic_widget.setFixedSize(430, 180)
        self.pic_widget.setPixmap(self.jpg_image)

        # the first way to manage the layout
        self.reminder01.move(477, 342)
        self.pic_widget.move(747, 785)

        # the second way to manage the layout but how to arrange them in Y axis?
        # self.main_layout = QVBoxLayout()
        # self.main_layout.addWidget(self.reminder01, alignment= Qt.AlignHCenter)
        # self.main_layout.addWidget(self.pic_widget, alignment= Qt.AlignHCenter)


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

        #
        self.main_widget = Singtel_StandbyLayout()
        self.setCentralWidget(self.main_widget)
        self.setGeometry(0, 0, 1920, 1080)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    sys.exit(app.exec_())
