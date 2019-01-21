# -*- coding: utf-8 -*-
"""
setStyleSheet('border: 1px solid black') or setStyleSheet('border: 1px dotted black') can show the border of rectangle.
setMask():
   It causes only the pixels of the widget for which bitmap has a corresponding 1 bit to be visible
   1, If setPen() is used in this case, setMask() cause some visible lines only.
   2. If setBrunsh() is used in this case, setMask() cause a visible region which is surrounded by those lines.

drawRoundedRect():
   It draws the given rectangle x, y, w, h with rounded corners.
   It might cause few points to be visible, which is not very accurate.

QDesktopWidget.availableGeometry():
   You can use QApplication.desktop() to return a QDesktopWidget.
   Returns the available geometry of the screen which contains widget.

QDesktopWidget.screenGeometry():
   Returns the geometry of the screen which contains widget.
"""

import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QBitmap, QPainter, QColor, QFontDatabase, QFont, QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QLabel, QFrame


class MyRoundedDialog(QDialog):

    def __init__(self, screen_width=1920, screen_height=1080, dialog_width=972, dialog_height=275,
                 mask_path = None, parent=None):
        super().__init__(parent=parent, flags=Qt.FramelessWindowHint)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.setFixedSize(dialog_width, dialog_height)
        # self.setStyleSheet('border: 1px solid red;')

        # a mask for showing a rounded rectangle zone
        if mask_path:
            # the second way to create the mask
            self.mask = QPixmap(mask_path)
            self.setMask(self.mask.mask())
            self.setFixedSize(self.mask.size())
        else:
            # first way to create the mask
            # print(self.size())  # (972, 275)  # This data might be used with
            # print(self.rect())  # (0, 0, 972, 275)
            self.mask_bitmap = QBitmap(self.size())
            self.bitmap_painter = QPainter(self.mask_bitmap)
            # self.bitmap_painter.setPen(QColor(255, 0, 0))
            self.bitmap_painter.setBrush(QColor(255, 0, 0))
            self.bitmap_painter.drawRoundedRect(self.rect(), 12, 12)
            self.setMask(self.mask_bitmap)
            del self.bitmap_painter  # to destroy it after drawing


class MyRoundedWidget(QFrame):

    def __init__(self, screen_width=1920, screen_height=1080, dialog_width=972, dialog_height=275,
                 mask_path = None, parent=None):
        super().__init__(parent=parent)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.setFixedSize(dialog_width, dialog_height)
        # self.setStyleSheet('border: 1px solid red;')

        # a mask for showing a rounded rectangle zone
        if mask_path:
            # the second way to create the mask
            self.mask = QPixmap(mask_path)
            self.setMask(self.mask.mask())
            self.setFixedSize(self.mask.size())
        else:
            # first way to create the mask
            # print(self.size())  # (972, 275)  # This data might be used with
            # print(self.rect())  # (0, 0, 972, 275)
            self.mask_bitmap = QBitmap(self.size())
            self.bitmap_painter = QPainter(self.mask_bitmap)
            # self.bitmap_painter.setPen(QColor(255, 0, 0))
            self.bitmap_painter.setBrush(QColor(255, 0, 0))
            self.bitmap_painter.drawRoundedRect(self.rect(), 12, 12)
            self.setMask(self.mask_bitmap)
            del self.bitmap_painter  # to destroy it after drawing


class ManyItemsError(MyRoundedDialog):

    def __init__(self, screen_width=1920, screen_height=1080, mask_path = './Images/ManyItemsError_mask.png', parent=None):
        super().__init__(screen_width=screen_width, screen_height=screen_height, mask_path=mask_path, parent=parent)

        #
        self.icon_widget = QLabel(self)
        self.icon_widget.setFixedSize(110, 110)
        self.icon_widget.setScaledContents(True)
        self.icon_pixmap = QPixmap()
        self.icon_pixmap.load('./Images/bigger_error_icon.png')
        self.icon_widget.setPixmap(self.icon_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setStyleSheet('''
            font-size: 48px;
            ''')
        self.title_widget.setFont(QFont('萍方-简'))
        self.title_widget.setText('More than 4 items detected')

        #
        self.reminder_widget = QLabel(self)
        self.reminder_widget.setStyleSheet('''
            font-size: 28px;
            color: #888888;
            ''')
        self.reminder_widget.setFont(QFont('萍方-简'))
        self.reminder_widget.setText('Place no more than 4 items at once')

        # layout management
        self.move(478, 400)
        self.icon_widget.move(90, 90)  # the movement is related to its parent. x_dialog + 115, y_dialog + 90
        self.title_widget.move(250, 90)
        self.reminder_widget.move(250, 164)


class ManyItemsError01(MyRoundedWidget):

    def __init__(self, screen_width=1920, screen_height=1080, mask_path = './Images/ManyItemsError_mask.png', parent=None):
        super().__init__(screen_width=screen_width, screen_height=screen_height, mask_path=mask_path, parent=parent)

        #
        self.icon_widget = QLabel(self)
        self.icon_widget.setFixedSize(110, 110)
        self.icon_widget.setScaledContents(True)
        self.icon_pixmap = QPixmap()
        self.icon_pixmap.load('./Images/bigger_error_icon.png')
        self.icon_widget.setPixmap(self.icon_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setStyleSheet('''
            font-size: 48px;
            ''')
        self.title_widget.setFont(QFont('萍方-简'))
        self.title_widget.setText('More than 4 items detected')

        #
        self.reminder_widget = QLabel(self)
        self.reminder_widget.setStyleSheet('''
            font-size: 28px;
            color: #888888;
            ''')
        self.reminder_widget.setFont(QFont('萍方-简'))
        self.reminder_widget.setText('Place no more than 4 items at once')

        # layout management
        self.move(478, 400)
        self.icon_widget.move(90, 90)  # the movement is related to its parent. x_dialog + 115, y_dialog + 90
        self.title_widget.move(250, 90)
        self.reminder_widget.move(250, 164)


class NetworkError(MyRoundedDialog):

    def __init__(self, screen_width=1920, screen_height=1080,  mask_path = './Images/NetworkError_mask.png',
                 parent=None):
        super().__init__(screen_width=screen_width, screen_height=screen_height, mask_path = mask_path,
                         dialog_width=int(1920*0.83), dialog_height=int(1080*0.21), parent=parent)
        #
        self.icon_widget = QLabel(self)
        self.icon_pixmap = QPixmap()
        self.icon_pixmap.load('./Images/error_icon.png')
        self.icon_widget.setPixmap(self.icon_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setScaledContents(True)
        self.title_widget.setStyleSheet('''
            font-size: 48px;
            color: #212121;
            ''')
        self.title_widget.setFont(QFont('萍方-简'))
        self.title_widget.setText('Unsuccessful operation due to network or other issues')

        # layout management
        self.move(150, 400)
        self.icon_widget.move(120, 73)  # the movement is related to its parent.
        self.title_widget.move(210, 73)  # x_icon + 70


class NetworkError01(MyRoundedWidget):

    def __init__(self, screen_width=1920, screen_height=1080,  mask_path = './Images/NetworkError_mask.png',
                 parent=None):
        super().__init__(screen_width=screen_width, screen_height=screen_height, mask_path = mask_path,
                         dialog_width=int(1920*0.83), dialog_height=int(1080*0.21), parent=parent)
        #
        self.icon_widget = QLabel(self)
        self.icon_pixmap = QPixmap()
        self.icon_pixmap.load('./Images/error_icon.png')
        self.icon_widget.setPixmap(self.icon_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setScaledContents(True)
        self.title_widget.setStyleSheet('''
            font-size: 48px;
            color: #212121;
            ''')
        self.title_widget.setFont(QFont('萍方-简'))
        self.title_widget.setText('Unsuccessful operation due to network or other issues')

        # layout management
        self.move(150, 400)
        self.icon_widget.move(120, 73)  # the movement is related to its parent.
        self.title_widget.move(210, 73)  # x_icon + 70


class DetectionIncorretError(MyRoundedDialog):

    def __init__(self, screen_width=1920, screen_height=1080, dialog_width=1326, dialog_height=822,
                 mask_path = './Images/DetectionIncorretError_mask.png', parent=None):
        super().__init__(screen_width=screen_width, screen_height=screen_height, mask_path = mask_path,
                         dialog_width=dialog_width, dialog_height=dialog_height,parent=parent)

        #
        self.icon_widget = QLabel(self)
        self.icon_pixmap = QPixmap()
        self.icon_pixmap.load('./Images/error_icon.png')
        self.icon_widget.setPixmap(self.icon_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setStyleSheet('''
            font-size: 48px;
            ''')
        self.title_widget.setFont(QFont('萍方-简'))
        self.title_widget.setText('Some items are not recognized.')

        #
        self.video_widget = QLabel(self)
        self.video_widget.setScaledContents(True)
        self.video_widget.setFixedSize(703, 470)
        self.video_widget.setAlignment(Qt.AlignCenter)
        self.correct_placing_gif = QMovie('./Images/correct_placing.gif')
        # self.correct_placing_gif.start()
        self.video_widget.setMovie(self.correct_placing_gif)

        #
        self.reminder_widget = QLabel(self)
        self.reminder_widget.setStyleSheet('''
            color: #888888;
            font-size: 28px;
            ''')
        self.reminder_widget.setFont(QFont('萍方-简'))
        self.reminder_widget.setText('Please place these items separately')

        #layout management
        self.move(306, 135)
        self.icon_widget.move(276, 73)  # the movement is related to its parent.
        self.title_widget.move(373, 73)
        self.video_widget.move(328, 214)
        self.reminder_widget.move(434, 720)


class DetectionIncorretError01(MyRoundedWidget):

    def __init__(self, screen_width=1920, screen_height=1080, dialog_width=1326, dialog_height=822,
                 mask_path = './Images/DetectionIncorretError_mask.png', parent=None):
        super().__init__(screen_width=screen_width, screen_height=screen_height, mask_path = mask_path,
                         dialog_width=dialog_width, dialog_height=dialog_height,parent=parent)

        #
        self.icon_widget = QLabel(self)
        self.icon_pixmap = QPixmap()
        self.icon_pixmap.load('./Images/error_icon.png')
        self.icon_widget.setPixmap(self.icon_pixmap)

        #
        self.title_widget = QLabel(self)
        self.title_widget.setStyleSheet('''
            font-size: 48px;
            ''')
        self.title_widget.setFont(QFont('萍方-简'))
        self.title_widget.setText('Some items are not recognized.')

        #
        self.video_widget = QLabel(self)
        self.video_widget.setScaledContents(True)
        self.video_widget.setFixedSize(703, 470)
        self.video_widget.setAlignment(Qt.AlignCenter)
        self.correct_placing_gif = QMovie('./Images/correct_placing.gif')
        # self.correct_placing_gif.start()
        self.video_widget.setMovie(self.correct_placing_gif)

        #
        self.reminder_widget = QLabel(self)
        self.reminder_widget.setStyleSheet('''
            color: #888888;
            font-size: 28px;
            ''')
        self.reminder_widget.setFont(QFont('萍方-简'))
        self.reminder_widget.setText('Please place these items separately')

        #layout management
        self.move(306, 135)
        self.icon_widget.move(276, 73)  # the movement is related to its parent.
        self.title_widget.move(373, 73)
        self.video_widget.move(328, 214)
        self.reminder_widget.move(434, 720)


class MyWindow(QMainWindow):
    def __init__(self, screen_width=1920, screen_height=1080):
        super().__init__()
        # adding special font
        singtel_font_database = QFontDatabase()
        singtel_font_database.addApplicationFont(r".\font\PingFang-SC.ttf")  # 萍方-简
        singtel_font_database.addApplicationFont(r".\font\WeChatSansSS-Medium.ttf")  # WeChat Sans SS Medium
        assert QFont.exactMatch(QFont('萍方-简'))  # to check whether the font can be used.
        assert QFont.exactMatch(QFont('WeChat Sans SS Medium'))  # to check whether the font can be used.
        # print(singtel_font_database.families())  # printing all supported font
        print('-----------------------adding special font successfully------------------------------------------')

        self.main_widget = QWidget()
        self.main_widget.setStyleSheet('background: black;')
        self.setGeometry(0, 0, 1920, 1080)
        self.setCentralWidget(self.main_widget)

        self.dialog01 = ManyItemsError(screen_width=screen_width, screen_height=screen_height)
        self.dialog01.show()

        self.dialog02 = NetworkError(screen_width=screen_width, screen_height=screen_height)
        self.dialog02.show()

        self.dialog03 = DetectionIncorretError(screen_width=screen_width, screen_height=screen_height)
        self.dialog03.show()
        self.dialog03.correct_placing_gif.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    current_desktop = QApplication.desktop()
    print('The current available geometry is %s' %current_desktop.availableGeometry()) # PyQt5.QtCore.QRect(0, 0, 1920, 1030)
    print('The current screnn geometryis %s' % current_desktop.screenGeometry()) # PyQt5.QtCore.QRect(0, 0, 1920, 1080)
    current_sreen = current_desktop.screenGeometry()
    mywindow = MyWindow(screen_width=current_sreen.width(), screen_height=current_sreen.height())
    mywindow.show()
    sys.exit(app.exec_())
