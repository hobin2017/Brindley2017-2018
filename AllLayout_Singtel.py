# -*- coding: utf-8 -*-
"""

"""
import logging
import sys

import cv2
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QFontDatabase, QFont, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QFrame, QStackedLayout, QPushButton, QDialog, \
    QGridLayout, QLabel

from CameraThread import MyCameraThread1_2
from ErrorReminder_Singtel import ManyItemsError, NetworkError, DetectionIncorretError
from ErrorReminder_Singtel import ManyItemsError01, NetworkError01, DetectionIncorretError01
from StandbyLayout_Singtel import Singtel_StandbyLayout
from MainLayout_Singtel import Singtel_LeftLayout, Singtel_RightLayout
from PayingLayout_Singtel import PayingLayout
from EndLayout_Singtel import PaySuccessLayout

class SingtelWindow(QMainWindow):

    def __init__(self, width_total=1920, height_total=1080, logger_name='hobin'):
        super().__init__()
        # QMainWindow settingc
        self.setStyleSheet('background: #F5F5F5;')
        self.layout().setContentsMargins(0, 0, 0, 0)  # If QMainWindow class is used
        self.layout().setSpacing(0)  # If QMainWindow class is used
        self.setGeometry(0, 0, width_total, height_total)

        # some variables
        self.standbylayout_stacked_index = 0
        self.mainlayout_stacked_index = 1
        self.mainlayout_right_stacked_shopping_index = 0
        self.mainlayout_right_stacked_buying_index = 1
        self.mainlayout_right_stacked_finishing_success_index = 2
        self.width_total = width_total
        self.height_total = height_total
        self.mylogger_topmost_ui = logging.getLogger(logger_name)

        # adding special font
        singtel_font_database = QFontDatabase()
        singtel_font_database.addApplicationFont(r".\font\PingFang-SC.ttf")  # 萍方-简
        singtel_font_database.addApplicationFont(r".\font\WeChatSansSS-Medium.ttf")  # WeChat Sans SS Medium
        assert QFont.exactMatch(QFont('萍方-简'))  # to check whether the font can be used.
        assert QFont.exactMatch(QFont('WeChat Sans SS Medium'))  # to check whether the font can be used.
        # print(singtel_font_database.families())  # printing all supported font
        self.mylogger_topmost_ui.info('adding special font successfully')

        self.layoutInit()
        self.error_reminder_Init()
        self.mylogger_topmost_ui.info('The initialization of widgets is successful')


    def layoutInit(self):
        # my layout widgets
        self.standbylayout_widget = Singtel_StandbyLayout()
        self.mainlayout_left_widget = Singtel_LeftLayout()
        self.mainlayout_right_widget01 = Singtel_RightLayout()
        self.mainlayout_right_widget02 = PayingLayout()
        self.mainlayout_right_widget03 = PaySuccessLayout()

        # main layout management
        self.mainlayout_right_stackedlayout = QStackedLayout()
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget01)
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget02)
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget03)
        self.mainlayout_right_stacked_widget = QFrame(self)
        self.mainlayout_right_stacked_widget.setLayout(self.mainlayout_right_stackedlayout)
        self.mainlayout_right_topmostlayout = QHBoxLayout()
        self.mainlayout_right_topmostlayout.addWidget(self.mainlayout_left_widget)
        self.mainlayout_right_topmostlayout.addWidget(self.mainlayout_right_stacked_widget)
        self.mainlayout_right_widget = QFrame(self)
        self.mainlayout_right_widget.setLayout(self.mainlayout_right_topmostlayout)

        # topmost layout management
        self.main_widget = QFrame(self)  # If QMainWindow class is used
        self.setCentralWidget(self.main_widget)  # If QMainWindow class is used
        self.topmost_layout = QStackedLayout()
        self.topmost_layout.addWidget(self.standbylayout_widget)
        self.topmost_layout.addWidget(self.mainlayout_right_widget)
        self.main_widget.setLayout(self.topmost_layout)  # If QMainWindow class is used

    def error_reminder_Init(self):
        self.dialog_many_items_error = ManyItemsError(screen_width=self.width_total, screen_height=self.height_total)
        self.dialog_network_error = NetworkError(screen_width=self.width_total, screen_height=self.height_total)
        self.dialog_detection_failure_error = DetectionIncorretError(screen_width=self.width_total, screen_height=self.height_total)

    def stopHandGif(self):
        """
        The account thread result might be no well matched user and you freeze the frame.
        What is more, a circling circle for showing thumbs-up is required to disappear.
        :return: 
        """
        self.mainlayout_right_widget01.frozen_frame_widget.hide()
        self.mainlayout_right_widget01.circle_gif.stop()
        self.mainlayout_right_widget01.circle_widget.hide()
        self.mainlayout_right_widget01.camera_widget.show()

    def toSettlement(self):
        """
        going to the main layout for the start of shopping
        :return:
        """
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_shopping_index)

    def hideErrorInfo(self):
        self.dialog_many_items_error.hide()
        self.dialog_network_error.hide()
        self.dialog_detection_failure_error.hide()

    def toWelcome(self):
        """
        going to the Standby layout
        :return:
        """
        self.topmost_layout.setCurrentIndex(self.standbylayout_stacked_index)

    def cleanCommodity(self):
        """
        It should be used with setSumPrice('0')
        :return:
        """
        self.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def setSumPrice(self, price):
        """

        :param price: str
        :return:
        """
        self.mainlayout_right_widget01.price_sum.setText('$' + price)

    def showErrorInfo(self, error_num=1):
        """
        if error_num=0, then DetectionIncorretError
        if error_num=1, then NetworkError
        if error_num=2, then ManyItemsError
        :param error_num: int
        :return:
        """
        if error_num == 0:
            self.dialog_detection_failure_error.show()
        elif error_num == 1:
            self.dialog_network_error.show()
        elif error_num == 2:
            self.dialog_many_items_error.show()

    def addCommodity(self, picid, name, image, price):
        """
        to display information about items
        :param picid: (int type) this is related to which Shopping_Unit instance
        :param name: (str type)
        :param image: (str type) the name of the image retrieved from database
        :param price: (str type)
        :return:
        """
        if picid == 0:
            # self.mainlayout_left_widget.shopping_unit01.pic_loader  # QPixmap for item image
            # self.mainlayout_left_widget.shopping_unit01.pic_widget # QLabel for item image
            self.mainlayout_left_widget.shopping_unit01.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit01.price_widget.setText(price)
            self.mainlayout_left_widget.shopping_unit01.show()
        elif picid == 1:
            # self.mainlayout_left_widget.shopping_unit02.pic_loader  # QPixmap for item image
            # self.mainlayout_left_widget.shopping_unit02.pic_widget  # QLabel for item image
            self.mainlayout_left_widget.shopping_unit02.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit02.price_widget.setText(price)
            self.mainlayout_left_widget.shopping_unit02.show()
        elif picid == 2:
            # self.mainlayout_left_widget.shopping_unit03.pic_loader  # QPixmap for item image
            # self.mainlayout_left_widget.shopping_unit03.pic_widget  # QLabel for item image
            self.mainlayout_left_widget.shopping_unit03.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit03.price_widget.setText(price)
            self.mainlayout_left_widget.shopping_unit03.show()
        elif picid == 3:
            # self.mainlayout_left_widget.shopping_unit04.pic_loader  # QLabel for item image
            # self.mainlayout_left_widget.shopping_unit04.pic_widget  # QLabel for item image
            self.mainlayout_left_widget.shopping_unit04.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit04.price_widget.setText(price)
            self.mainlayout_left_widget.shopping_unit04.show()

    def toPayingView(self, image=None):
        """
        going to the Paying layout
        :param image: (QImage type)
        :return:
        """
        if image:
            temp_pixmap = self.mainlayout_right_widget02.head_pixmap.fromImage(image)
            self.mainlayout_right_widget02.head_widget.setPixmap(temp_pixmap)
            self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
            self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_shopping_index)

    def toRegisterView(self, image=None, qrimage=None):
        """
        The user can not pay by face pay.
        :param image: (ndarray type)
        :param qrimage: (PIL.ImageQt.ImageQt class which is like QIamge class)
        :return:
        """
        pass

    def toPaySuccessView(self, image=None, name = None):
        """
        The transaction is successful.
        :param image:
        :param name:
        :return:
        """
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_finishing_success_index)

    def toPayFailView(self, image= None, name= None):
        """
        The transaction is not successful
        :param image:
        :param name:
        :return:
        """
        pass

    def showHandGif(self, x, y, frame, width=200):
        """
        to display the frozen frame with a gif
        :param x: the x of the center point for circling thumbs-up
        :param y: the y of the circle point for circling thumbs-up
        :param frame: the frozen frame
        :param width: ??
        :return:
        """
        self.mainlayout_right_widget01.camera_widget.hide()
        temp_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
        temp_height, temp_width, channel = temp_img.shape  # width=640, height=480
        bytes_per_line = 3 * temp_width
        temp_pixmap = self.mainlayout_right_widget01.frozen_frame_pixmap.fromImage(
            QImage(temp_img.data, temp_width, temp_height, bytes_per_line, QImage.Format_RGB888).mirrored(horizontal=True, vertical=False))
        self.mainlayout_right_widget01.frozen_frame_widget.setPixmap(temp_pixmap)
        self.mainlayout_right_widget01.frozen_frame_widget.show()
        self.mainlayout_right_widget01.circle_widget.move(x, y)
        self.mainlayout_right_widget01.circle_gif.start()


class SingtelWindow01(QFrame):
    """
    It is a complete widget for Klas_Singtel_V1_1_0.py file
    Compared with SingtelWindow, the topmost layout changes since it inherits from QFrame class.
    Compared with SingtelWindow, the closeEvent is defined in this class since it receives the close signal.
    """
    def __init__(self, parent=None, width_total=1920, height_total=1080, logger_name='hobin',**kwargs):
        super().__init__()
        # QMainWindow settingc
        self.setStyleSheet('background: #F5F5F5;')
        # self.setGeometry(0, 0, width_total, height_total)
        self.showFullScreen()

        # some variables
        self.standbylayout_stacked_index = 0
        self.mainlayout_stacked_index = 1
        self.mainlayout_right_stacked_shopping_index = 0
        self.mainlayout_right_stacked_buying_index = 1
        self.mainlayout_right_stacked_finishing_success_index = 2
        self.width_total = width_total
        self.height_total = height_total
        self.parent = parent
        self.mylogger_topmost_ui = logging.getLogger(logger_name)

        # adding special font
        singtel_font_database = QFontDatabase()
        singtel_font_database.addApplicationFont(r"./font/PingFang-SC.ttf")  # 萍方-简
        singtel_font_database.addApplicationFont(r"./font/WeChatSansSS-Medium.ttf")  # WeChat Sans SS Medium
        # print(singtel_font_database.families())  # printing all supported font
        # assert QFont.exactMatch(QFont('萍方-简'))  # to check whether the font can be used. It might be failed since it is not simplified Chinese.
        # assert QFont.exactMatch(QFont('WeChat Sans SS Medium'))  # to check whether the font can be used.
        self.mylogger_topmost_ui.info('adding special font successfully')

        #
        self.mysetting_layout = kwargs
        self.mysetting_layout['font_family01'] = '萍方-简'
        self.mylogger_topmost_ui.info('layout setting is %s' % self.mysetting_layout)

        self.layoutInit()
        self.error_reminder_Init()
        self.mylogger_topmost_ui.info('The initialization of widgets is successful')


    def preprocess_work(self):
        """
        It is used in the Klas(Singtel)_V1_0_0.py to hide some widgets and to start the gif.
        :return:
        """
        # hiding all shopping items
        self.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

        # a black and half-transparent decoration for the main layout
        self.mainlayout_decoration_widget.hide()

        # starting the gif
        self.mainlayout_right_widget01.circle_gif.start()
        self.mainlayout_right_widget01.thumbs_up_gif.start()
        self.mainlayout_right_widget02.head_decoration_gif.start()
        self.mainlayout_right_widget02.loading_gif.start()
        self.dialog_detection_failure_error.correct_placing_gif.start()

    def layoutInit(self):
        # my layout widgets
        self.standbylayout_widget = Singtel_StandbyLayout(**self.mysetting_layout)
        self.mainlayout_left_widget = Singtel_LeftLayout(**self.mysetting_layout)
        self.mainlayout_right_widget01 = Singtel_RightLayout(**self.mysetting_layout)
        self.mainlayout_right_widget02 = PayingLayout(**self.mysetting_layout)
        self.mainlayout_right_widget03 = PaySuccessLayout(**self.mysetting_layout)

        # main layout management
        self.mainlayout_right_stackedlayout = QStackedLayout()
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget01)
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget02)
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget03)
        self.mainlayout_right_stacked_widget = QFrame(self)
        self.mainlayout_right_stacked_widget.setLayout(self.mainlayout_right_stackedlayout)
        self.mainlayout_right_topmostlayout = QHBoxLayout()
        self.mainlayout_right_topmostlayout.addWidget(self.mainlayout_left_widget)
        self.mainlayout_right_topmostlayout.addWidget(self.mainlayout_right_stacked_widget)
        self.mainlayout_right_widget = QFrame(self)
        self.mainlayout_right_widget.setLayout(self.mainlayout_right_topmostlayout)

        #
        self.mainlayout_decoration_widget = QLabel(self.mainlayout_right_widget)
        self.mainlayout_decoration_widget.setFixedSize(1920, 1080)
        self.mainlayout_decoration_widget.setStyleSheet('background-color: rgba(0,0,0,50%);')

        # topmost layout management
        self.topmost_layout = QStackedLayout()
        self.topmost_layout.addWidget(self.standbylayout_widget)
        self.topmost_layout.addWidget(self.mainlayout_right_widget)
        self.setLayout(self.topmost_layout)

    def error_reminder_Init(self):
        self.dialog_many_items_error = ManyItemsError(screen_width=self.width_total, screen_height=self.height_total, parent=self)
        self.dialog_network_error = NetworkError(screen_width=self.width_total, screen_height=self.height_total, parent=self)
        self.dialog_detection_failure_error = DetectionIncorretError(screen_width=self.width_total, screen_height=self.height_total, parent=self)

    def stopHandGif(self):
        """
        The account thread result might be no well matched user and you freeze the frame.
        What is more, a circling circle for showing thumbs-up is required to disappear.
        :return:
        """
        self.mylogger_topmost_ui.info('stopHandGif starts')
        self.mainlayout_right_widget01.frozen_frame_widget.hide()
        self.mainlayout_right_widget01.circle_gif.stop()
        self.mainlayout_right_widget01.circle_widget.hide()
        self.mainlayout_right_widget01.camera_widget.show()
        self.mylogger_topmost_ui.info('stopHandGif ends')

    def toSettlement(self):
        """
        going to the main layout for the start of shopping
        :return:
        """
        self.mylogger_topmost_ui.info('toSettlement starts')
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_shopping_index)
        self.mylogger_topmost_ui.info('toSettlement ends')

    def hideErrorInfo(self):
        self.mainlayout_decoration_widget.hide()
        self.dialog_many_items_error.hide()
        self.dialog_network_error.hide()
        self.dialog_detection_failure_error.hide()

    def toWelcome(self):
        """
        going to the Standby layout
        :return:
        """
        self.mylogger_topmost_ui.info('toWelcome starts')
        self.topmost_layout.setCurrentIndex(self.standbylayout_stacked_index)
        self.mylogger_topmost_ui.info('toWelcome ends')

    def cleanCommodity(self):
        """
        It should be used with setSumPrice('0')
        :return:
        """
        self.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def setSumPrice(self, price):
        """

        :param price: str
        :return:
        """
        self.mainlayout_right_widget01.price_sum.setText('$' + price)

    def showErrorInfo(self, error_num=1):
        """
        if error_num=0, then DetectionIncorretError
        if error_num=1, then NetworkError
        if error_num=2, then ManyItemsError
        :param error_num: int
        :return:
        """
        self.mainlayout_decoration_widget.show()
        if error_num == 0:
            self.dialog_network_error.hide()
            self.dialog_many_items_error.hide()
            self.dialog_detection_failure_error.show()
        elif error_num == 1:
            self.dialog_many_items_error.hide()
            self.dialog_detection_failure_error.hide()
            self.dialog_network_error.show()
        elif error_num == 2:
            self.dialog_network_error.hide()
            self.dialog_detection_failure_error.hide()
            self.dialog_many_items_error.show()

    def addCommodity(self, picid, name, image, price):
        """
        to display information about items
        :param picid: (int type) this is related to which Shopping_Unit instance
        :param name: (str type)
        :param image: (str type) the value is the same as the sku_id
        :param price: (str type)
        :return:
        """
        temp_qpixmap = self.parent.item_images_dict.get(image)
        text_length = 30
        if len(name) > text_length:
            name = name[:text_length] + '...'
        if picid == 1:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit01.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit01.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit01.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit01.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit01.show()
        elif picid == 2:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit02.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit02.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit02.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit02.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit02.show()
        elif picid == 3:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit03.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit03.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit03.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit03.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit03.show()
        elif picid == 4:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit04.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit04.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit04.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit04.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit04.show()

    def toPayingView(self, image=None):
        """
        going to the Paying layout
        :param image: (QImage type)
        :return:
        """
        self.mylogger_topmost_ui.info('toPayingView starts')
        if image:
            self.mylogger_topmost_ui.info('The image object is not None.')
            temp_pixmap = self.mainlayout_right_widget02.head_pixmap.fromImage(image)
            self.mainlayout_right_widget02.head_widget.setPixmap(temp_pixmap)
            # self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)  # In logic, this requirement is satisified.
            self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_buying_index)
        else:
            # the account_work17_klas function does not pass object to the image object which indicates there is no user detected.
            pass
        self.mylogger_topmost_ui.info('toPayingView ends')

    def toRegisterView(self, image=None, qrimage=None):
        """
        The user can not pay by face pay.
        :param image: (ndarray type)
        :param qrimage: (PIL.ImageQt.ImageQt class which is like QIamge class)
        :return:
        """
        self.mylogger_topmost_ui.info('toRegisterView starts')
        self.mylogger_topmost_ui.info('toRegisterView ends')

    def toPaySuccessView(self, image=None, name = None):
        """
        The transaction is successful.
        :param image:
        :param name:
        :return:
        """
        self.mylogger_topmost_ui.info('toPaySuccessView starts')
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_finishing_success_index)
        self.mylogger_topmost_ui.info('toPaySuccessView ends')

    def toPayFailView(self, image= None, name= None):
        """
        The transaction is not successful
        :param image:
        :param name:
        :return:
        """
        self.mylogger_topmost_ui.info('toPayFailView starts')
        self.mylogger_topmost_ui.info('toPayFailView ends')

    def showHandGif(self, x, y, frame, length=200):
        """
        to display the frozen frame with a gif
        :param x: the x of the center point for circling thumbs-up
        :param y: the y of the circle point for circling thumbs-up
        :param length: the maximum value of w and h for that detected rectangle.
        :param frame: the frozen frame
        :param circle_radius: to calculate the position of the top left point
        :return:
        """
        self.mylogger_topmost_ui.info('showHandGif starts')
        self.mainlayout_right_widget01.camera_widget.hide()
        temp_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
        temp_height, temp_width, channel = temp_img.shape
        bytes_per_line = 3 * temp_width
        temp_pixmap = self.mainlayout_right_widget01.frozen_frame_pixmap.fromImage(
            QImage(temp_img.data, temp_width, temp_height, bytes_per_line, QImage.Format_RGB888).mirrored(horizontal=True, vertical=False))
        self.mainlayout_right_widget01.frozen_frame_widget.setPixmap(temp_pixmap)
        self.mainlayout_right_widget01.frozen_frame_widget.show()  # to refresh the widget actively
        approximate_x, approximate_y = self.calculate_location_HangGif(frame_width=temp_width, frame_height=temp_height,
                                                                       radius=int(length/2), offset_x=x, offset_y=y,
                                                                       mirror_type='h')
        self.mainlayout_right_widget01.circle_widget.resize(length, length)
        self.mainlayout_right_widget01.circle_widget.show()  # to refresh the widget actively
        self.mainlayout_right_widget01.circle_widget.move(approximate_x, approximate_y)
        self.mainlayout_right_widget01.circle_gif.start()
        self.mylogger_topmost_ui.info('showHandGif ends')

    def calculate_location_HangGif(self, frame_width, frame_height, radius, offset_x=0, offset_y=0, mirror_type=None):
        self.mylogger_topmost_ui.info('calculate_location_HangGif starts')
        self.mylogger_topmost_ui.info('x: %s, y: %s, frame_width: %s, frame_height: %s'
                                      %(offset_x, offset_y, frame_width, frame_height))
        # step 1: to calculate the center point of the circle gif after the mirror operation
        if mirror_type == 'h':
            # horizontal mirrored
            x1 = frame_width - offset_x
            y1 = offset_y
        elif mirror_type == 'v':
            # vertical mirrored
            x1 = offset_x
            y1 = frame_height - offset_y
        elif mirror_type == 'hv' or mirror_type == 'vh':
            # horizontal and vertical mirrored
            x1 = frame_width - offset_x
            y1 = frame_height - offset_y
        else:
            # not mirrored operation
            x1 = offset_x
            y1 = offset_y
        self.mylogger_topmost_ui.info('step 2: (%s, %s)' % (x1, y1))

        # step 2: to calculate the topmost left point of the circle gif
        x2 = x1 - radius
        y2 = y1 - radius
        self.mylogger_topmost_ui.info('step 2: (%s, %s)' % (x2, y2))

        # step 3: to calculate the he topmost left point of the circle gif after resizing operation
        # the formula is like 'x_after/ x_before = widget_width / frame_width'
        x3 = x2 / frame_width * self.mainlayout_right_widget01.frozen_frame_widget.width()
        y3 = y2 / frame_height * self.mainlayout_right_widget01.frozen_frame_widget.height()
        self.mylogger_topmost_ui.info('(w, h) of frozen_frame_widget is (%s, %s)'
                                      %(self.mainlayout_right_widget01.frozen_frame_widget.width(),
                                        self.mainlayout_right_widget01.frozen_frame_widget.height())
                                      )
        self.mylogger_topmost_ui.info('step 3: (%s, %s)' % (x3, y3))

        # step 4: doing addition since the gif widget uses relative coordination.
        approximate_x = int(x3+ self.mainlayout_right_widget01.frozen_frame_widget.x())
        approximate_y = int(y3+ self.mainlayout_right_widget01.frozen_frame_widget.y())
        self.mylogger_topmost_ui.info('(x, y) of frozen_frame_widget is (%s, %s)'
                                      % (self.mainlayout_right_widget01.frozen_frame_widget.x(),
                                         self.mainlayout_right_widget01.frozen_frame_widget.y())
                                      )
        self.mylogger_topmost_ui.info('calculate_location_HangGif ends with (%s, %s)' % (approximate_x, approximate_y))
        return (approximate_x, approximate_y)

    def closeEvent(self, event):
        self.mylogger_topmost_ui.info('%s starts to close widgets' %self.__class__)
        # print(event)  # The result is like <PyQt5.QtGui.QCloseEvent object at 0x0000022FE39C6B88>
        self.dialog_many_items_error.close()
        self.dialog_network_error.close()
        self.dialog_detection_failure_error.close()
        self.parent.closeEvent(event)
        super().closeEvent(event)


class SingtelWindow02(QFrame):
    """
    Compared with SingtelWindow01, all error reminder widget are QFrame class since QDialog always be at the topmost level.
And the parent of these error reminder are the main layout widget to prevent their appearance in standby layout.
    """
    def __init__(self, parent=None, width_total=1920, height_total=1080, logger_name='hobin',**kwargs):
        super().__init__()
        # QMainWindow settingc
        self.setStyleSheet('background: #F5F5F5;')
        # self.setGeometry(0, 0, width_total, height_total)
        self.showFullScreen()

        # some variables
        self.standbylayout_stacked_index = 0
        self.mainlayout_stacked_index = 1
        self.mainlayout_right_stacked_shopping_index = 0
        self.mainlayout_right_stacked_buying_index = 1
        self.mainlayout_right_stacked_finishing_success_index = 2
        self.width_total = width_total
        self.height_total = height_total
        self.parent = parent
        self.mylogger_topmost_ui = logging.getLogger(logger_name)

        # adding special font
        singtel_font_database = QFontDatabase()
        singtel_font_database.addApplicationFont(r"./font/PingFang-SC.ttf")  # 萍方-简
        singtel_font_database.addApplicationFont(r"./font/WeChatSansSS-Medium.ttf")  # WeChat Sans SS Medium
        # print(singtel_font_database.families())  # printing all supported font
        # assert QFont.exactMatch(QFont('萍方-简'))  # to check whether the font can be used. It might be failed since it is not simplified Chinese.
        # assert QFont.exactMatch(QFont('WeChat Sans SS Medium'))  # to check whether the font can be used.
        self.mylogger_topmost_ui.info('adding special font successfully')

        #
        self.mysetting_layout = kwargs
        self.mysetting_layout['font_family01'] = '萍方-简'
        self.mylogger_topmost_ui.info('layout setting is %s' % self.mysetting_layout)

        self.layoutInit()
        self.error_reminder_Init()
        self.mylogger_topmost_ui.info('The initialization of widgets is successful')


    def preprocess_work(self):
        """
        It is used in the Klas(Singtel)_V1_0_0.py to hide some widgets and to start the gif.
        :return:
        """
        # hiding all shopping items
        self.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

        # a black and half-transparent decoration for the main layout
        self.mainlayout_decoration_widget.hide()

        # starting the gif
        self.mainlayout_right_widget01.circle_gif.start()
        self.mainlayout_right_widget01.thumbs_up_gif.start()
        self.mainlayout_right_widget02.head_decoration_gif.start()
        self.mainlayout_right_widget02.loading_gif.start()
        self.dialog_detection_failure_error.correct_placing_gif.start()

    def layoutInit(self):
        # my layout widgets
        self.standbylayout_widget = Singtel_StandbyLayout(**self.mysetting_layout)
        self.mainlayout_left_widget = Singtel_LeftLayout(**self.mysetting_layout)
        self.mainlayout_right_widget01 = Singtel_RightLayout(**self.mysetting_layout)
        self.mainlayout_right_widget02 = PayingLayout(**self.mysetting_layout)
        self.mainlayout_right_widget03 = PaySuccessLayout(**self.mysetting_layout)

        # main layout management
        self.mainlayout_right_stackedlayout = QStackedLayout()
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget01)
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget02)
        self.mainlayout_right_stackedlayout.addWidget(self.mainlayout_right_widget03)
        self.mainlayout_right_stacked_widget = QFrame(self)
        self.mainlayout_right_stacked_widget.setLayout(self.mainlayout_right_stackedlayout)
        self.mainlayout_topmostlayout = QHBoxLayout()
        self.mainlayout_topmostlayout.addWidget(self.mainlayout_left_widget)
        self.mainlayout_topmostlayout.addWidget(self.mainlayout_right_stacked_widget)
        self.mainlayout_widget = QFrame(self)
        self.mainlayout_widget.setLayout(self.mainlayout_topmostlayout)

        #
        self.mainlayout_decoration_widget = QLabel(self.mainlayout_widget)
        self.mainlayout_decoration_widget.setFixedSize(1920, 1080)
        self.mainlayout_decoration_widget.setStyleSheet('background-color: rgba(0,0,0,50%);')

        # topmost layout management
        self.topmost_layout = QStackedLayout()
        self.topmost_layout.addWidget(self.standbylayout_widget)
        self.topmost_layout.addWidget(self.mainlayout_widget)
        self.setLayout(self.topmost_layout)

    def error_reminder_Init(self):
        self.dialog_many_items_error = ManyItemsError01(screen_width=self.width_total, screen_height=self.height_total,
                                                      parent=self.mainlayout_widget)
        self.dialog_network_error = NetworkError01(screen_width=self.width_total, screen_height=self.height_total,
                                                 parent=self.mainlayout_widget)
        self.dialog_detection_failure_error = DetectionIncorretError01(screen_width=self.width_total,
                                                                     screen_height=self.height_total,
                                                                     parent=self.mainlayout_widget)

    def stopHandGif(self):
        """
        The account thread result might be no well matched user and you freeze the frame.
        What is more, a circling circle for showing thumbs-up is required to disappear.
        :return:
        """
        self.mylogger_topmost_ui.info('stopHandGif starts')
        self.mainlayout_right_widget01.frozen_frame_widget.hide()
        self.mainlayout_right_widget01.circle_gif.stop()
        self.mainlayout_right_widget01.circle_widget.hide()
        self.mainlayout_right_widget01.camera_widget.show()
        self.mylogger_topmost_ui.info('stopHandGif ends')

    def toSettlement(self):
        """
        going to the main layout for the start of shopping
        :return:
        """
        self.mylogger_topmost_ui.info('toSettlement starts')
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_shopping_index)
        self.mylogger_topmost_ui.info('toSettlement ends')

    def hideErrorInfo(self):
        self.mainlayout_decoration_widget.hide()
        self.dialog_many_items_error.hide()
        self.dialog_network_error.hide()
        self.dialog_detection_failure_error.hide()

    def toWelcome(self):
        """
        going to the Standby layout
        :return:
        """
        self.mylogger_topmost_ui.info('toWelcome starts')
        self.topmost_layout.setCurrentIndex(self.standbylayout_stacked_index)
        self.mylogger_topmost_ui.info('toWelcome ends')

    def cleanCommodity(self):
        """
        It should be used with setSumPrice('0')
        :return:
        """
        self.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def setSumPrice(self, price):
        """

        :param price: str
        :return:
        """
        self.mainlayout_right_widget01.price_sum.setText('$' + price)

    def showErrorInfo(self, error_num=1):
        """
        if error_num=0, then DetectionIncorretError
        if error_num=1, then NetworkError
        if error_num=2, then ManyItemsError
        :param error_num: int
        :return:
        """
        self.mainlayout_decoration_widget.show()
        if error_num == 0:
            self.dialog_network_error.hide()
            self.dialog_many_items_error.hide()
            self.dialog_detection_failure_error.show()
        elif error_num == 1:
            self.dialog_many_items_error.hide()
            self.dialog_detection_failure_error.hide()
            self.dialog_network_error.show()
        elif error_num == 2:
            self.dialog_network_error.hide()
            self.dialog_detection_failure_error.hide()
            self.dialog_many_items_error.show()

    def addCommodity(self, picid, name, image, price):
        """
        to display information about items
        :param picid: (int type) this is related to which Shopping_Unit instance
        :param name: (str type)
        :param image: (str type) the value is the same as the sku_id
        :param price: (str type)
        :return:
        """
        temp_qpixmap = self.parent.item_images_dict.get(image)
        text_length = 30
        if len(name) > text_length:
            name = name[:text_length] + '...'
        if picid == 1:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit01.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit01.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit01.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit01.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit01.show()
        elif picid == 2:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit02.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit02.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit02.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit02.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit02.show()
        elif picid == 3:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit03.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit03.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit03.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit03.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit03.show()
        elif picid == 4:
            if temp_qpixmap:
                self.mainlayout_left_widget.shopping_unit04.pic_widget.setPixmap(temp_qpixmap)
            else:
                self.mainlayout_left_widget.shopping_unit04.pic_widget.setPixmap(self.mainlayout_left_widget.default_item_image)
            self.mainlayout_left_widget.shopping_unit04.name_widget.setText(name)
            self.mainlayout_left_widget.shopping_unit04.price_widget.setText('$%s' %price)
            self.mainlayout_left_widget.shopping_unit04.show()

    def toPayingView(self, image=None):
        """
        going to the Paying layout
        :param image: (QImage type)
        :return:
        """
        self.mylogger_topmost_ui.info('toPayingView starts')
        if image:
            self.mylogger_topmost_ui.info('The image object is not None.')
            temp_pixmap = self.mainlayout_right_widget02.head_pixmap.fromImage(image)
            self.mainlayout_right_widget02.head_widget.setPixmap(temp_pixmap)
            # self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)  # In logic, this requirement is satisified.
            self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_buying_index)
        else:
            # the account_work17_klas function does not pass object to the image object which indicates there is no user detected.
            pass
        self.mylogger_topmost_ui.info('toPayingView ends')

    def toRegisterView(self, image=None, qrimage=None):
        """
        The user can not pay by face pay.
        :param image: (ndarray type)
        :param qrimage: (PIL.ImageQt.ImageQt class which is like QIamge class)
        :return:
        """
        self.mylogger_topmost_ui.info('toRegisterView starts')
        self.mylogger_topmost_ui.info('toRegisterView ends')

    def toPaySuccessView(self, image=None, name = None):
        """
        The transaction is successful.
        :param image:
        :param name:
        :return:
        """
        self.mylogger_topmost_ui.info('toPaySuccessView starts')
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_finishing_success_index)
        self.mylogger_topmost_ui.info('toPaySuccessView ends')

    def toPayFailView(self, image= None, name= None):
        """
        The transaction is not successful
        :param image:
        :param name:
        :return:
        """
        self.mylogger_topmost_ui.info('toPayFailView starts')
        self.mylogger_topmost_ui.info('toPayFailView ends')

    def showHandGif(self, x, y, frame, length=200):
        """
        to display the frozen frame with a gif
        :param x: the x of the center point for circling thumbs-up
        :param y: the y of the circle point for circling thumbs-up
        :param length: the maximum value of w and h for that detected rectangle.
        :param frame: the frozen frame
        :param circle_radius: to calculate the position of the top left point
        :return:
        """
        self.mylogger_topmost_ui.info('showHandGif starts')
        self.mainlayout_right_widget01.camera_widget.hide()
        temp_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
        temp_height, temp_width, channel = temp_img.shape
        bytes_per_line = 3 * temp_width
        temp_pixmap = self.mainlayout_right_widget01.frozen_frame_pixmap.fromImage(
            QImage(temp_img.data, temp_width, temp_height, bytes_per_line, QImage.Format_RGB888).mirrored(horizontal=True, vertical=False))
        self.mainlayout_right_widget01.frozen_frame_widget.setPixmap(temp_pixmap)
        self.mainlayout_right_widget01.frozen_frame_widget.show()  # to refresh the widget actively
        approximate_x, approximate_y = self.calculate_location_HangGif(frame_width=temp_width, frame_height=temp_height,
                                                                       radius=int(length/2), offset_x=x, offset_y=y,
                                                                       mirror_type='h')
        self.mainlayout_right_widget01.circle_widget.resize(length, length)
        self.mainlayout_right_widget01.circle_widget.show()  # to refresh the widget actively
        self.mainlayout_right_widget01.circle_widget.move(approximate_x, approximate_y)
        self.mainlayout_right_widget01.circle_gif.start()
        self.mylogger_topmost_ui.info('showHandGif ends')

    def calculate_location_HangGif(self, frame_width, frame_height, radius, offset_x=0, offset_y=0, mirror_type=None):
        self.mylogger_topmost_ui.info('calculate_location_HangGif starts')
        self.mylogger_topmost_ui.info('x: %s, y: %s, frame_width: %s, frame_height: %s'
                                      %(offset_x, offset_y, frame_width, frame_height))
        # step 1: to calculate the center point of the circle gif after the mirror operation
        if mirror_type == 'h':
            # horizontal mirrored
            x1 = frame_width - offset_x
            y1 = offset_y
        elif mirror_type == 'v':
            # vertical mirrored
            x1 = offset_x
            y1 = frame_height - offset_y
        elif mirror_type == 'hv' or mirror_type == 'vh':
            # horizontal and vertical mirrored
            x1 = frame_width - offset_x
            y1 = frame_height - offset_y
        else:
            # not mirrored operation
            x1 = offset_x
            y1 = offset_y
        self.mylogger_topmost_ui.info('step 2: (%s, %s)' % (x1, y1))

        # step 2: to calculate the topmost left point of the circle gif
        x2 = x1 - radius
        y2 = y1 - radius
        self.mylogger_topmost_ui.info('step 2: (%s, %s)' % (x2, y2))

        # step 3: to calculate the he topmost left point of the circle gif after resizing operation
        # the formula is like 'x_after/ x_before = widget_width / frame_width'
        x3 = x2 / frame_width * self.mainlayout_right_widget01.frozen_frame_widget.width()
        y3 = y2 / frame_height * self.mainlayout_right_widget01.frozen_frame_widget.height()
        self.mylogger_topmost_ui.info('(w, h) of frozen_frame_widget is (%s, %s)'
                                      %(self.mainlayout_right_widget01.frozen_frame_widget.width(),
                                        self.mainlayout_right_widget01.frozen_frame_widget.height())
                                      )
        self.mylogger_topmost_ui.info('step 3: (%s, %s)' % (x3, y3))

        # step 4: doing addition since the gif widget uses relative coordination.
        approximate_x = int(x3+ self.mainlayout_right_widget01.frozen_frame_widget.x())
        approximate_y = int(y3+ self.mainlayout_right_widget01.frozen_frame_widget.y())
        self.mylogger_topmost_ui.info('(x, y) of frozen_frame_widget is (%s, %s)'
                                      % (self.mainlayout_right_widget01.frozen_frame_widget.x(),
                                         self.mainlayout_right_widget01.frozen_frame_widget.y())
                                      )
        self.mylogger_topmost_ui.info('calculate_location_HangGif ends with (%s, %s)' % (approximate_x, approximate_y))
        return (approximate_x, approximate_y)

    def closeEvent(self, event):
        self.mylogger_topmost_ui.info('%s starts to close widgets' %self.__class__)
        # print(event)  # The result is like <PyQt5.QtGui.QCloseEvent object at 0x0000022FE39C6B88>
        self.dialog_many_items_error.close()
        self.dialog_network_error.close()
        self.dialog_detection_failure_error.close()
        self.parent.closeEvent(event)
        super().closeEvent(event)


class TestWindow(SingtelWindow):

    def __init__(self):
        super().__init__()
        self.standbylayout_stacked_index = 0
        self.mainlayout_stacked_index =1
        self.mainlayout_right_stacked_shopping_index =0
        self.mainlayout_right_stacked_buying_index = 1
        self.mainlayout_right_stacked_finishing_success_index = 2
        self.test_camera_thread()
        self.test_gif()
        self.dialog_init()


    def test_camera_thread(self):
        self.user_capture01 = cv2.VideoCapture(0)
        self.user_capture01.set(3, self.width_total)
        self.user_capture01.set(4, self.height_total)
        self.cam_thread = MyCameraThread1_2(camera_object=self.user_capture01)
        self.cam_thread.update.connect(self.mainlayout_right_widget01.camera_widget.refresh)
        self.cam_thread.start()

    def test_gif(self):
        self.mainlayout_right_widget01.circle_gif.start()
        self.mainlayout_right_widget01.thumbs_up_gif.start()
        self.mainlayout_right_widget02.head_decoration_gif.start()
        self.mainlayout_right_widget02.loading_gif.start()
        self.dialog_detection_failure_error.correct_placing_gif.start()

    def dialog_init(self):
        # the control unit(QDialog) for the main layout
        self.dialog01 = QDialog()
        self.dialog01.setFixedSize(300, 300)
        #
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
        self.button06 = QPushButton('Go standby')
        self.button06.clicked.connect(self.goStandby)
        self.button07 = QPushButton('Go main')
        self.button07.clicked.connect(self.goShopping)
        self.button08 = QPushButton('Go processing')
        self.button08.clicked.connect(self.goProcessing)
        self.button09 = QPushButton('Go end')
        self.button09.clicked.connect(self.goEnd)
        self.button10 = QPushButton('show ManyItemsError')
        self.button10.clicked.connect(self.showManyItemsError)
        self.button11 = QPushButton('hide ManyItemsError')
        self.button11.clicked.connect(self.hideManyItemsError)
        self.button12 = QPushButton('show NetworkError')
        self.button12.clicked.connect(self.showNetworkError)
        self.button13 = QPushButton('hide NetworkError')
        self.button13.clicked.connect(self.hideNetworkError)
        self.button14 = QPushButton('show DetectionIncorretError')
        self.button14.clicked.connect(self.showDetectionIncorretError)
        self.button15 = QPushButton('hide DetectionIncorretError')
        self.button15.clicked.connect(self.hideDetectionIncorretError)
        self.button16 = QPushButton('freeze frame')
        self.button16.clicked.connect(self.freezeFrame)
        self.button17 = QPushButton('unfreeze frame')
        self.button17.clicked.connect(self.unfreezeFrame)

        # layout management of the QDialog
        self.dialog01_main_layout = QGridLayout()
        self.dialog01.setLayout(self.dialog01_main_layout)
        self.dialog01_main_layout.addWidget(self.button01, 1, 1)
        self.dialog01_main_layout.addWidget(self.button02, 2, 1)
        self.dialog01_main_layout.addWidget(self.button03, 2, 2)
        self.dialog01_main_layout.addWidget(self.button04, 3, 1)
        self.dialog01_main_layout.addWidget(self.button05, 3, 2)
        self.dialog01_main_layout.addWidget(self.button06, 4, 1)
        self.dialog01_main_layout.addWidget(self.button07, 4, 2)
        self.dialog01_main_layout.addWidget(self.button08, 5, 1)
        self.dialog01_main_layout.addWidget(self.button09, 5, 2)
        self.dialog01_main_layout.addWidget(self.button10, 6, 1)
        self.dialog01_main_layout.addWidget(self.button11, 6, 2)
        self.dialog01_main_layout.addWidget(self.button12, 7, 1)
        self.dialog01_main_layout.addWidget(self.button13, 7, 2)
        self.dialog01_main_layout.addWidget(self.button14, 8, 1)
        self.dialog01_main_layout.addWidget(self.button15, 8, 2)
        self.dialog01_main_layout.addWidget(self.button16, 9, 1)
        self.dialog01_main_layout.addWidget(self.button17, 9, 2)
        self.dialog01.show()

    def showAllItems(self):
        self.mainlayout_left_widget.shopping_unit01.setVisible(True)
        self.mainlayout_left_widget.shopping_unit02.setVisible(True)
        self.mainlayout_left_widget.shopping_unit03.setVisible(True)
        self.mainlayout_left_widget.shopping_unit04.setVisible(True)

    def hideOne(self):
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def hideTwo(self):
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def hideThree(self):
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def hideFour(self):
        self.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def goStandby(self):
        self.topmost_layout.setCurrentIndex(self.standbylayout_stacked_index)

    def goShopping(self):
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_shopping_index)

    def goProcessing(self):
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_buying_index)

    def goEnd(self):
        self.topmost_layout.setCurrentIndex(self.mainlayout_stacked_index)
        self.mainlayout_right_stackedlayout.setCurrentIndex(self.mainlayout_right_stacked_finishing_success_index)

    def freezeFrame(self):
        self.mainlayout_right_widget01.camera_widget.hide()
        self.mainlayout_right_widget01.frozen_frame_widget.setStyleSheet('background: yellow;')
        self.mainlayout_right_widget01.frozen_frame_widget.show()
        self.mainlayout_right_widget01.circle_widget.show()
        self.mainlayout_right_widget01.circle_gif.start()

    def unfreezeFrame(self):
        self.mainlayout_right_widget01.frozen_frame_widget.hide()
        self.mainlayout_right_widget01.circle_gif.stop()
        self.mainlayout_right_widget01.circle_widget.hide()
        self.mainlayout_right_widget01.camera_widget.show()

    def showManyItemsError(self):
        self.dialog_many_items_error.show()

    def hideManyItemsError(self):
        self.dialog_many_items_error.hide()

    def showNetworkError(self):
        self.dialog_network_error.show()

    def hideNetworkError(self):
        self.dialog_network_error.hide()

    def showDetectionIncorretError(self):
        self.dialog_detection_failure_error.show()

    def hideDetectionIncorretError(self):
        self.dialog_detection_failure_error.hide()

    def closeEvent(self, event):
        # print(event)  # The result is like <PyQt5.QtGui.QCloseEvent object at 0x0000022FE39C6B88>
        self.cam_thread.status = False
        self.user_capture01.release()
        super().closeEvent(event)  # using the closeEvent function of the QWidget class.


class TestWindow02(QObject):
    """
    Compared with TestWindow class, the widget is used inside this class.
    Compared with TestWindow class, the closeEvent() differs: the SingtelWindow01 class is the first one to receives
the close signal and then I call the TestWindow02.closeEvent().
    """
    def __init__(self):
        super().__init__()
        self.width_total =1920
        self.height_total = 1080
        self.main_window = SingtelWindow02(parent=self)
        self.test_camera_thread()
        self.test_gif()
        self.dialog_init()

    def test_camera_thread(self):
        self.user_capture01 = cv2.VideoCapture(0)
        self.user_capture01.set(3, self.width_total)
        self.user_capture01.set(4, self.height_total)
        self.cam_thread = MyCameraThread1_2(camera_object=self.user_capture01)
        self.cam_thread.update.connect(self.main_window.mainlayout_right_widget01.camera_widget.refresh)
        self.cam_thread.start()

    def test_gif(self):
        self.main_window.mainlayout_right_widget01.circle_gif.start()
        self.main_window.mainlayout_right_widget01.thumbs_up_gif.start()
        self.main_window.mainlayout_right_widget02.head_decoration_gif.start()
        self.main_window.mainlayout_right_widget02.loading_gif.start()
        self.main_window.dialog_detection_failure_error.correct_placing_gif.start()

    def dialog_init(self):
        # the control unit(QDialog) for the main layout
        self.dialog01 = QDialog()
        self.dialog01.setFixedSize(300, 300)
        #
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
        self.button06 = QPushButton('Go standby')
        self.button06.clicked.connect(self.goStandby)
        self.button07 = QPushButton('Go main')
        self.button07.clicked.connect(self.goShopping)
        self.button08 = QPushButton('Go processing')
        self.button08.clicked.connect(self.goProcessing)
        self.button09 = QPushButton('Go end')
        self.button09.clicked.connect(self.goEnd)
        self.button10 = QPushButton('show ManyItemsError')
        self.button10.clicked.connect(self.showManyItemsError)
        self.button11 = QPushButton('hide ManyItemsError')
        self.button11.clicked.connect(self.hideManyItemsError)
        self.button12 = QPushButton('show NetworkError')
        self.button12.clicked.connect(self.showNetworkError)
        self.button13 = QPushButton('hide NetworkError')
        self.button13.clicked.connect(self.hideNetworkError)
        self.button14 = QPushButton('show DetectionIncorretError')
        self.button14.clicked.connect(self.showDetectionIncorretError)
        self.button15 = QPushButton('hide DetectionIncorretError')
        self.button15.clicked.connect(self.hideDetectionIncorretError)
        self.button16 = QPushButton('freeze frame')
        self.button16.clicked.connect(self.freezeFrame)
        self.button17 = QPushButton('unfreeze frame')
        self.button17.clicked.connect(self.unfreezeFrame)
        self.button18 = QPushButton('show decoration')
        self.button18.clicked.connect(self.showDecoration)
        self.button19 = QPushButton('hide decoration')
        self.button19.clicked.connect(self.hideDecoration)

        # layout management of the QDialog
        self.dialog01_main_layout = QGridLayout()
        self.dialog01.setLayout(self.dialog01_main_layout)
        self.dialog01_main_layout.addWidget(self.button01, 1, 1)
        self.dialog01_main_layout.addWidget(self.button02, 2, 1)
        self.dialog01_main_layout.addWidget(self.button03, 2, 2)
        self.dialog01_main_layout.addWidget(self.button04, 3, 1)
        self.dialog01_main_layout.addWidget(self.button05, 3, 2)
        self.dialog01_main_layout.addWidget(self.button06, 4, 1)
        self.dialog01_main_layout.addWidget(self.button07, 4, 2)
        self.dialog01_main_layout.addWidget(self.button08, 5, 1)
        self.dialog01_main_layout.addWidget(self.button09, 5, 2)
        self.dialog01_main_layout.addWidget(self.button10, 6, 1)
        self.dialog01_main_layout.addWidget(self.button11, 6, 2)
        self.dialog01_main_layout.addWidget(self.button12, 7, 1)
        self.dialog01_main_layout.addWidget(self.button13, 7, 2)
        self.dialog01_main_layout.addWidget(self.button14, 8, 1)
        self.dialog01_main_layout.addWidget(self.button15, 8, 2)
        self.dialog01_main_layout.addWidget(self.button16, 9, 1)
        self.dialog01_main_layout.addWidget(self.button17, 9, 2)
        self.dialog01_main_layout.addWidget(self.button18, 10, 1)
        self.dialog01_main_layout.addWidget(self.button19, 10, 2)
        self.dialog01.show()

    def showAllItems(self):
        self.main_window.mainlayout_left_widget.shopping_unit01.setVisible(True)
        self.main_window.mainlayout_left_widget.shopping_unit02.setVisible(True)
        self.main_window.mainlayout_left_widget.shopping_unit03.setVisible(True)
        self.main_window.mainlayout_left_widget.shopping_unit04.setVisible(True)

    def hideOne(self):
        self.main_window.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def hideTwo(self):
        self.main_window.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.main_window.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def hideThree(self):
        self.main_window.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.main_window.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.main_window.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def hideFour(self):
        self.main_window.mainlayout_left_widget.shopping_unit01.setHidden(True)
        self.main_window.mainlayout_left_widget.shopping_unit02.setHidden(True)
        self.main_window.mainlayout_left_widget.shopping_unit03.setHidden(True)
        self.main_window.mainlayout_left_widget.shopping_unit04.setHidden(True)

    def goStandby(self):
        self.main_window.topmost_layout.setCurrentIndex(self.main_window.standbylayout_stacked_index)

    def goShopping(self):
        self.main_window.topmost_layout.setCurrentIndex(self.main_window.mainlayout_stacked_index)
        self.main_window.mainlayout_right_stackedlayout.setCurrentIndex(
            self.main_window.mainlayout_right_stacked_shopping_index)

    def goProcessing(self):
        self.main_window.topmost_layout.setCurrentIndex(self.main_window.mainlayout_stacked_index)
        self.main_window.mainlayout_right_stackedlayout.setCurrentIndex(
            self.main_window.mainlayout_right_stacked_buying_index)

    def goEnd(self):
        self.main_window.topmost_layout.setCurrentIndex(self.main_window.mainlayout_stacked_index)
        self.main_window.mainlayout_right_stackedlayout.setCurrentIndex(
            self.main_window.mainlayout_right_stacked_finishing_success_index)

    def freezeFrame(self):
        self.main_window.mainlayout_right_widget01.camera_widget.hide()
        self.main_window.mainlayout_right_widget01.frozen_frame_widget.setStyleSheet('background: yellow;')
        self.main_window.mainlayout_right_widget01.frozen_frame_widget.show()
        self.main_window.mainlayout_right_widget01.circle_widget.show()
        self.main_window.mainlayout_right_widget01.circle_gif.start()

    def unfreezeFrame(self):
        self.main_window.mainlayout_right_widget01.frozen_frame_widget.hide()
        self.main_window.mainlayout_right_widget01.circle_gif.stop()
        self.main_window.mainlayout_right_widget01.circle_widget.hide()
        self.main_window.mainlayout_right_widget01.camera_widget.show()

    def showManyItemsError(self):
        self.main_window.dialog_many_items_error.show()

    def hideManyItemsError(self):
        self.main_window.dialog_many_items_error.hide()

    def showNetworkError(self):
        self.main_window.dialog_network_error.show()

    def hideNetworkError(self):
        self.main_window.dialog_network_error.hide()

    def showDetectionIncorretError(self):
        self.main_window.dialog_detection_failure_error.show()

    def hideDetectionIncorretError(self):
        self.main_window.dialog_detection_failure_error.hide()

    def showDecoration(self):
        self.main_window.mainlayout_decoration_widget.show()

    def hideDecoration(self):
        self.main_window.mainlayout_decoration_widget.hide()

    def closeEvent(self, event):
        # print(event)  # The result is like <PyQt5.QtGui.QCloseEvent object at 0x0000022FE39C6B88>
        self.cam_thread.status = False
        self.user_capture01.release()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # mywindow = TestWindow()
    # mywindow.show()
    mytest01 = TestWindow02()
    mytest01.main_window.show()
    sys.exit(app.exec_())

