# -*- coding: utf-8 -*-
"""
setStyleSheet('border: 1px solid black') or setStyleSheet('border: 1px dotted black') can show the border of rectangle.
   1, You can use the html tags <p> to display a text with multiple-line format in QLabel widget;
   2, The QFrame class is the subclass of QWidget that can have a frame. The frame style is specified by a frame shape
(NoFrame, Box, Panel, StyledPanel, HLine and VLine) and a shadow style (Plain, Raised and Sunken) that is used to
visually separate the frame from surrounding widgets. These properties can be set together using the setFrameStyle()
function and read with frameStyle().
   3, Using setStyleSheet() to decorate the QWidget-like widget;
   4, border: 1px solid black; 1px dotted black;
"""
import sys

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie, QFontDatabase, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QLabel, QFrame, QPushButton, \
    QDialog, QGridLayout

from CameraLayout import CameraWidget3
from CameraThread import MyCameraThread1_2

class Singtel_MainLayout(QWidget):
    """
    Be careful, the actual layout will differ.
    """
    def __init__(self, width=1920, height=1080):
        super().__init__()
        self.width = width
        self.height = height
        # self.setStyleSheet('border: 1px dotted black')
        self.setFixedSize(width, height)
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout01 = QHBoxLayout()
        self.main_layout01.setSpacing(0)
        self.main_layout01.setContentsMargins(0, 0, 0, 0)
        # I force the Singtel_LeftLayout class have fixed size.
        # And the size of Singtel_RightLayout is calculated automatically by the QHBoxLayout..
        self.main_layout02 = Singtel_LeftLayout()
        self.main_layout03 = Singtel_RightLayout()

        #
        self.main_layout01.addWidget(self.main_layout02)
        self.main_layout01.addWidget(self.main_layout03)
        self.setLayout(self.main_layout01)


class Singtel_LeftLayout(QWidget):

    def __init__(self, width=1920, height=1080, *, font_family01='萍方-简', font_family02='WeChat Sans SS Medium', **kwargs):
        super().__init__()
        print('font_family01 of Singtel_LeftLayout is %s' %font_family01)
        print('font_family02 of Singtel_LeftLayout is %s' % font_family02)
        self.width = width
        self.height = height
        self.setFixedSize(1380, self.height)
        self.setContentsMargins(0, 0, 0, 0)

        # Use the keyword 'margin' and 'spacing' to beatify the user_interface.
        self.shopping_unit01 = Shopping_Unit(self, font_family01=font_family01, font_family02=font_family02)
        self.shopping_unit01.move(0, 30)
        self.shopping_unit02 = Shopping_Unit(self, font_family01=font_family01, font_family02=font_family02)
        self.shopping_unit02.move(0, 290)
        self.shopping_unit03 = Shopping_Unit(self, font_family01=font_family01, font_family02=font_family02)
        self.shopping_unit03.move(0, 550)
        self.shopping_unit04 = Shopping_Unit(self, font_family01=font_family01, font_family02=font_family02)
        self.shopping_unit04.move(0, 810)

        # default item image
        self.default_item_image = QPixmap('./Images/999.jpg')


class Shopping_Unit(QFrame):
    """
    If you use QFrame, the setStyleSheet('background: white;') only has effects for its children.
    """
    def __init__(self, parent=None, width=1920, height=1080, font_family01='萍方-简', font_family02='WeChat Sans SS Medium'):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.setFixedSize(1380, 240)
        # The setting 'margin: 10, 20, 30, 40;' indicates the top, right, bottom and left margin;
        # This will have effects on its child widget;
        self.setStyleSheet('''
            background: white; 
            margin-top: 0px;
            margin-right: 58px;
            margin-bottom: 0px;
            margin-left: 58px;
            ''')

        #
        self.fraction_width_pic = 0.095
        self.fraction_height_pic = 0.17
        self.pic_widget = QLabel(self)
        self.pic_widget.setScaledContents(True)
        self.pic_widget.setStyleSheet('''
           margin-top: 0px;
           margin-right: 0px;
           margin-bottom: 0px;
           margin-left: 0px;
           ''')
        # print(self.pic_widget.getContentsMargins())  # (0, 0, 0, 0) by default.
        self.pic_widget.setFixedSize(int(width*self.fraction_width_pic), int(height*self.fraction_height_pic))
        self.pic_loader = QPixmap()
        self.pic_loader.load('./Images/define.jpg')
        self.pic_widget.setPixmap(self.pic_loader)
        self.pic_widget.move(91, 31)

        #
        self.fraction_width_name = 0.295
        self.fraction_height_name = 0.05
        self.name_widget = QLabel(self)
        self.name_widget.setFont(QFont(font_family01))
        self.name_widget.setStyleSheet('''
            font-size: 36px; 
            margin-top: 0px;
            margin-right: 0px;
            margin-bottom: 0px;
            margin-left: 0px;
            ''')
        self.name_widget.setFixedSize(int(width*self.fraction_width_name), int(height*self.fraction_height_name))
        self.name_widget.setText('Item Name')
        self.name_widget.move(300, 95)

        #
        self.price_widget = QLabel(self)
        self.price_widget.setScaledContents(True)
        self.price_widget.setFont(QFont(font_family02))
        self.price_widget.setStyleSheet('''
            font-size:60px; 
            margin-top: 0px;
            margin-right: 0px;
            margin-bottom: 0px;
            margin-left: 0px;
            ''')
        self.price_widget.setFixedSize(215, 65)
        self.price_widget.setText('$10.00')
        self.price_widget.move(1100, 90)

        # Currently, these three widgets are arranged by absolute layout mangement.
        # The second way is using QLayout to manage them.
        # self.main_layout01 = QHBoxLayout()
        # # print(self.main_layout01.getContentsMargins())  # Why it is (0,0,0,0) not (11, 11, 11, 11)? This is a bug?
        # self.main_layout01.setContentsMargins(0, 0, 0, 0)
        # self.main_layout01.setSpacing(0)
        # self.main_layout01.addWidget(self.pic_widget, alignment=Qt.AlignVCenter)
        # self.main_layout01.addWidget(self.name_widget, alignment=Qt.AlignVCenter)
        # self.main_layout01.addWidget(self.price_widget, alignment=Qt.AlignRight)
        # self.setLayout(self.main_layout01)


class Singtel_RightLayout(QFrame):

    def __init__(self, width=1920, height=1080, *, font_family01='萍方-简', font_family02='WeChat Sans SS Medium', **kwargs):
        super().__init__()
        print('font_family01 of Singtel_RightLayout is %s' % font_family01)
        print('font_family02 of Singtel_RightLayout is %s' % font_family02)
        self.width = width
        self.height = height
        self.setStyleSheet('''
            background: white; 
            ''')
        self.setFixedSize(540, 1080)

        #
        self.fraction_width_price_reminder = 0.05
        self.fraction_height_price_reminder = 0.05
        self.price_reminder = QLabel(self)
        self.price_reminder.setFont(QFont(font_family01))
        self.price_reminder.setStyleSheet('''
            font-size: 36px;
            ''')
        self.price_reminder.setFixedSize(int(self.width * self.fraction_width_price_reminder),
                                         int(self.height * self.fraction_height_price_reminder))
        self.price_reminder.setText('Total')
        self.price_reminder.setAlignment(Qt.AlignCenter)

        #
        self.fraction_width_price_sum = 0.15
        self.fraction_height_price_sum = 0.08
        self.price_sum = QLabel(self)
        self.price_sum.setFont(QFont(font_family02))
        self.price_sum.setStyleSheet('''
            font-size: 80px;
            ''')
        self.price_sum.setFixedSize(int(self.width * self.fraction_width_price_sum),
                                    int(self.height * self.fraction_height_price_sum))
        self.price_sum.setText('$0.0')
        self.price_sum.setAlignment(Qt.AlignCenter)

        #
        self.shopping_reminder01 = QLabel(self)
        self.shopping_reminder01.setFont(QFont(font_family01))
        self.shopping_reminder01.setStyleSheet('''
            font-size: 20px;
            color: #888888;
            ''')
        self.shopping_reminder01.setFixedSize(216, 33)
        self.shopping_reminder01.setAlignment(Qt.AlignCenter)
        self.shopping_reminder01.setText('For demonstration only')

        #
        self.camera_widget = CameraWidget3(self)
        self.camera_widget.setScaledContents(True)  # to scale its contents to fill all available space.
        self.camera_widget.setFixedSize(437, 328)
        self.camera_widget.setAlignment(Qt.AlignCenter)

        #
        self.frozen_frame_pixmap = QPixmap()
        self.frozen_frame_widget = QLabel(self)
        self.frozen_frame_widget.setScaledContents(True)
        self.frozen_frame_widget.setFixedSize(437, 328)
        self.frozen_frame_widget.setAlignment(Qt.AlignCenter)

        #
        self.circle_gif = QMovie('./Images/circling_thumbs_up.gif')
        self.circle_widget = QLabel(self)
        self.circle_widget.setStyleSheet('background-color: 255;')
        self.circle_widget.setScaledContents(True)
        self.circle_widget.setFixedSize(121, 121)
        self.circle_widget.setMovie(self.circle_gif)

        #
        self.sublayout_video = QHBoxLayout()
        self.sublayout_video.setSpacing(0)
        self.sublayout_video.setContentsMargins(0, 0, 0, 0)
        self.sublayout_video.setAlignment(Qt.AlignHCenter)
        #
        self.video_widget = QLabel()
        self.thumbs_up_gif = QMovie('./Images/showing_thumbs.gif')
        # self.thumbs_up_gif.start()  # It should start when showing the main layout and stop when showing other layout.
        self.video_widget.setMovie(self.thumbs_up_gif)
        self.video_widget.setFixedSize(142, 259)
        self.video_widget.setAlignment(Qt.AlignCenter)
        #
        self.fraction_width_shopping_reminder02 = 0.12
        self.fraction_height_shopping_reminder02 = 0.20
        self.shopping_reminder02 = QLabel()
        self.shopping_reminder02.setFont(QFont(font_family01))
        self.shopping_reminder02.setStyleSheet('''
            font-size: 28px;
            margin-right: 30px;
            color: #888888;
            ''')
        self.shopping_reminder02.setText('''
        <p>Thumbs-Up</p>
        <p>Gesture</p>
        <p>Payment</p>
        ''')
        self.shopping_reminder02.setAlignment(Qt.AlignCenter)

        # layout management
        temp_alignment = Qt.AlignHCenter
        self.sublayout_video.addWidget(self.shopping_reminder02, alignment=temp_alignment)
        self.sublayout_video.addWidget(self.video_widget, alignment=temp_alignment)
        self.shopping_reminder02_1 = QFrame(self)
        self.shopping_reminder02_1.setLayout(self.sublayout_video)

        self.price_reminder.move(228, 118)
        self.price_sum.move(120, 179)
        self.shopping_reminder01.move(165, 272)
        self.frozen_frame_widget.move(52, 345)
        self.frozen_frame_widget.hide()
        self.circle_widget.move(52, 345)
        self.circle_widget.hide()
        self.camera_widget.move(52, 345)
        self.shopping_reminder02_1.move(73, 703)


class TestingWindow(QMainWindow):
    """
    This Window is used for the Singtel_MainLayout class.
    """
    def __init__(self, width=1920, height=1080, cam_capture_width=640, cam_capture_height=480,
                 cam_widget_width=400, cam_widget_height=350):
        super(TestingWindow, self).__init__()
        # adding special font
        singtel_font_database = QFontDatabase()
        singtel_font_database.addApplicationFont(r".\font\PingFang-SC.ttf") # 萍方-简
        singtel_font_database.addApplicationFont(r".\font\WeChatSansSS-Medium.ttf")  # WeChat Sans SS Medium
        assert QFont.exactMatch(QFont('萍方-简'))  # to check whether the font can be used.
        assert QFont.exactMatch(QFont('WeChat Sans SS Medium'))  # to check whether the font can be used.
        # print(singtel_font_database.families())  # printing all supported font
        print('-----------------------adding special font successfully------------------------------------------')

        # the QMainWindow setting
        self.setStyleSheet('background: #F5F5F5;')
        # print(self.layout().getContentsMargins())  # Why it is (13, 13, 13, 13) but not (11, 11, 11, 11)?
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.setGeometry(0, 0, width, height)
        self.main_widget = Singtel_MainLayout()
        self.setCentralWidget(self.main_widget)

        #
        self.user_capture01 = cv2.VideoCapture(0)
        self.user_capture01.set(3, cam_capture_width)
        self.user_capture01.set(4, cam_capture_height)
        self.cam_thread = MyCameraThread1_2(camera_object=self.user_capture01)
        self.cam_thread.update.connect(self.main_widget.main_layout03.camera_widget.refresh)

        # the control unit(QDialog) for the main layout
        self.dialog01 = QDialog()
        self.dialog01.setFixedSize(300, 300)
        self.dialog01_main_layout = QGridLayout()
        self.button01 = QPushButton('show all')
        self.button01.clicked.connect(self.showAllItems)
        self.button02 = QPushButton('hide 1')
        self.button02.clicked.connect(self.hideOne)
        self.button03 = QPushButton('hide 2')
        self.button03.clicked.connect(self.hideTwo)
        self.button04 = QPushButton('hide 3')
        self.button04.clicked.connect(self.hideThree)
        self.button05 = QPushButton('hide 4')
        self.button05.clicked.connect(self.hideFour)

        # layout management of the QDialog
        self.dialog01.setLayout(self.dialog01_main_layout)
        self.dialog01_main_layout.addWidget(self.button01)
        self.dialog01_main_layout.addWidget(self.button02)
        self.dialog01_main_layout.addWidget(self.button03)
        self.dialog01_main_layout.addWidget(self.button04)
        self.dialog01_main_layout.addWidget(self.button05)
        self.dialog01.show()

        # starts to work
        self.main_widget.main_layout03.thumbs_up_gif.start()
        self.main_widget.main_layout03.circle_gif.start()
        self.cam_thread.start()


    def showAllItems(self):
        self.main_widget.main_layout02.shopping_unit01.setVisible(True)
        self.main_widget.main_layout02.shopping_unit02.setVisible(True)
        self.main_widget.main_layout02.shopping_unit03.setVisible(True)
        self.main_widget.main_layout02.shopping_unit04.setVisible(True)

    def hideOne(self):
        self.main_widget.main_layout02.shopping_unit04.setHidden(True)

    def hideTwo(self):
        self.main_widget.main_layout02.shopping_unit03.setHidden(True)
        self.main_widget.main_layout02.shopping_unit04.setHidden(True)

    def hideThree(self):
        self.main_widget.main_layout02.shopping_unit02.setHidden(True)
        self.main_widget.main_layout02.shopping_unit03.setHidden(True)
        self.main_widget.main_layout02.shopping_unit04.setHidden(True)

    def hideFour(self):
        self.main_widget.main_layout02.shopping_unit01.setHidden(True)
        self.main_widget.main_layout02.shopping_unit02.setHidden(True)
        self.main_widget.main_layout02.shopping_unit03.setHidden(True)
        self.main_widget.main_layout02.shopping_unit04.setHidden(True)

    def closeEvent(self, event):
        # print(event)  # The result is like <PyQt5.QtGui.QCloseEvent object at 0x0000022FE39C6B88>
        self.cam_thread.status = False
        self.user_capture01.release()
        self.dialog01.close()
        super().closeEvent(event)  # using the closeEvent function of the QWidget class.


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = TestingWindow()
    mywindow.show()
    sys.exit(app.exec_())

