# -*- coding: utf-8 -*-
"""

"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame


class PayingLayout(QFrame):

    def __init__(self, *, font_family01='萍方-简', **kwargs):
        super().__init__()
        print('font_family01 of PayingLayout is %s' % font_family01)
        self.setStyleSheet('''
            background: white;
            ''')

        #
        self.title_widget = QLabel(self)
        self.title_widget.setStyleSheet('''
            font-size: 30px;
            color: #4A4A4A;
            ''')
        self.title_widget.setFont(QFont(font_family01))
        self.title_widget.setAlignment(Qt.AlignCenter)
        self.title_widget.setText('Facial Recognition Payment')

        #
        self.head_pixmap = QPixmap()
        self.head_widget = QLabel(self)
        self.head_widget.setStyleSheet('background: yellow;')
        self.head_widget.setScaledContents(True)
        self.head_widget.setFixedSize(215, 215)
        # self.head_widget.setPixmap(self.head_pixmap)

        #
        self.head_decoration_gif = QMovie('./Images/face_paying.gif')
        self.head_decoration_widget = QLabel(self.head_widget)
        self.head_decoration_widget.setStyleSheet('background: 255;')
        self.head_decoration_widget.setScaledContents(True)
        self.head_decoration_widget.setFixedSize(215, 215)
        self.head_decoration_widget.setMovie(self.head_decoration_gif)

        #
        self.shopping_reminder = QLabel(self)
        self.shopping_reminder.setStyleSheet('''
            font-size: 28px;
            color: #888888;
            ''')
        self.shopping_reminder.setFont(QFont(font_family01))
        self.shopping_reminder.setAlignment(Qt.AlignCenter)
        self.shopping_reminder.setText('Purchasing')

        #
        self.loading_gif = QMovie('./Images/loading.gif')
        self.waiting_reminder = QLabel(self)
        self.waiting_reminder.setScaledContents(True)
        self.waiting_reminder.setMovie(self.loading_gif)


        # layout management
        self.title_widget.move(80, 275)
        self.head_widget.move(163, 370)
        self.shopping_reminder.move(195, 615)
        self.waiting_reminder.move(230, 675)


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
        self.main_widget = PayingLayout()
        self.main_widget.setFixedSize(540, 1080)
        self.setCentralWidget(self.main_widget)

        #
        self.main_widget.head_decoration_gif.start()
        self.main_widget.loading_gif.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    sys.exit(app.exec_())
