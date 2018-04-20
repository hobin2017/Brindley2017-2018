"""
author = hobin
"""
import cv2
import os

import sys
from PyQt5.QtCore import QSizeF, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtWidgets import QGraphicsView, QLabel, QGraphicsScene, QVBoxLayout, QDialog, QApplication, QHBoxLayout
from PyQt5.QtMultimedia import QCameraInfo, QCamera
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from CameraThread import MyCameraThread1


class CameraWidget1(QGraphicsView):
    """
    QGraphicsView uses QGraphicsScene by 'setScene';
    QGraphicsScene uses QGraphicsVideoItem by 'addItem';
    QGraphicsVideoItem is also used by QCamera according to 'setViewfinder';
    problem: the camera only be shown by mousePressEvent or keyPressEvent. I don't know why.
    """

    def __init__(self, parent=None):
        super(CameraWidget1, self).__init__(parent)

        size_info = self.geometry()  # QRect class
        self.x = size_info.x()
        self.y = size_info.y()
        self.width = size_info.width()
        self.height = size_info.height()
        self.scene = QGraphicsScene(self.x, self.y, self.width, self.height)
        self.setScene(self.scene)  # to visualize the QGraphicsScene
        self.videoItem1 = QGraphicsVideoItem()  # QGraphicsVideoItem actually is a subclass of the QGraphicsItem class
        self.videoItem1.setSize(QSizeF(self.width,
                                       self.height))  # QGraphicsVideoItem will draw video scaled to fit size according to its fillMode.
        self.videoItem1.setPos(self.x, self.y)  # the setPos() function can be checked in QGraphicsItem class.
        self.scene.addItem(
            self.videoItem1)  # QGraphicsScene can add your existing QGraphicsItem objects by calling addItem()
        # QCamera can be used with QCameraViewfinder for viewfinder display, QMediaRecorder for video recording and QCameraImageCapture for image taking.
        self.camera1 = QCamera(QCameraInfo.defaultCamera(), self)
        self.camera1.setViewfinder(
            self.videoItem1)  # The parameter could be QVideoWidget, QGraphicsVideoItem and QAbstractVideoSurface.
        # The capture mode only could be QCamera.CaptureViewfinder, CaptureStillImage and CaptureVideo.
        # self.camera1.setCaptureMode(QCamera.CaptureVideo)
        self.camera1.setCaptureMode(QCamera.CaptureViewfinder)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # do not show horizontal scroll bar.

    def mousePressEvent(self, event):
        if self.camera1.state == QCamera.ActiveState:
            self.camera1.stop()
        else:
            self.camera1.start()


class CameraWidget2(QLabel):
    """
    The QLabel is refreshed by its own QThread.
    """
    def __init__(self, parent=None):
        super(CameraWidget2, self).__init__(parent)
        self.capture0 = cv2.VideoCapture(0)
        self.capture0.set(3, 600)  # 3 indicates the width;
        self.capture0.set(4, 450)  # 4 indicates the height;
        self.thread1 = MyCameraThread1(camera_object=self.capture0, parent=self) # The index of camera should be given carefully.
        self.thread1.update.connect(self.refresh)
        self.thread1.start()


    def refresh(self, img):
        self.setPixmap(QPixmap.fromImage(img)) # the type of img is QImage


class CameraWidget2_1(QLabel):
    """
    The QLabel is refreshed by its own QThread.
    """
    def __init__(self, parent=None):
        super(CameraWidget2_1, self).__init__(parent)
        self.setScaledContents(True)
        self.capture0 = cv2.VideoCapture(0)
        self.capture0.set(3, 600)  # 3 indicates the width;
        self.capture0.set(4, 450)  # 4 indicates the height;
        self.thread1 = MyCameraThread1(camera_object=self.capture0, parent=self) # The index of camera should be given carefully.
        self.thread1.update.connect(self.refresh)
        #
        self.icon01 = QLabel(self)
        self.movie = QMovie('.\\images\\handpay3.gif')
        self.icon01.setMovie(self.movie)
        self.mainlayout = QVBoxLayout(self)
        self.mainlayout.addWidget(self.icon01)
        self.mainlayout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        #
        self.setLayout(self.mainlayout)
        self.icon01.setVisible(False)
        self.movie.start()
        self.thread1.start()


    def refresh(self, img):
        self.setPixmap(QPixmap.fromImage(img)) # the type of img is QImage


class CameraWidget2_2(QLabel):
    """
    The QLabel is refreshed by its own QThread.
    The file path can be used both on windows and linux.
    The camera is initialized by the keyword argument kwargs.
    """
    def __init__(self, parent=None, **kwargs):
        super(CameraWidget2_2, self).__init__(parent)
        # all file path configuration
        dir_path = os.path.dirname(__file__)
        gif_path = os.path.join(dir_path, 'Images', 'handpay3.gif')
        self.setScaledContents(True)
        self.capture0 = cv2.VideoCapture(int(kwargs['cam_num']))
        self.capture0.set(3, int(kwargs['width']))  # 3 indicates the width;
        self.capture0.set(4, int(kwargs['height']))  # 4 indicates the height;
        self.thread1 = MyCameraThread1(camera_object=self.capture0, parent=self) # The index of camera should be given carefully.
        self.thread1.update.connect(self.refresh)
        #
        self.icon01 = QLabel(self)
        self.movie = QMovie(gif_path)
        self.icon01.setMovie(self.movie)
        self.mainlayout = QVBoxLayout(self)
        self.mainlayout.addWidget(self.icon01)
        self.mainlayout.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        #
        self.setLayout(self.mainlayout)
        self.icon01.setVisible(False)
        self.movie.start()
        self.thread1.start()


    def refresh(self, img):
        self.setPixmap(QPixmap.fromImage(img)) # the type of img is QImage


class CameraWidget2_3(QLabel):
    """
    This class is used to display the image of the item camera.
    Compared with the CameraWidget2 class, the main difference is that the camera is provided from outside.
    """
    def __init__(self, camera_object):
        super(CameraWidget2_3, self).__init__()
        self.capture = camera_object
        self.mainlayout = QHBoxLayout()
        self.label = QLabel()
        self.mainlayout.addWidget(self.label)
        self.setLayout(self.mainlayout)
        self.thread1 = MyCameraThread1(camera_object=self.capture, parent=self)  # The index of camera should be given carefully.
        self.thread1.update.connect(self.refresh)
        self.thread1.start()


    def refresh(self, img):
        self.label.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage


class CameraDialog(QDialog):
    """
    This class is used to display the image of the item camera.
    """
    def __init__(self, camera_object):
        super(CameraDialog, self).__init__()
        self.capture = camera_object
        self.setWindowTitle('Item Camera in Brindley')
        self.mainlayout = QHBoxLayout()
        self.label = QLabel()
        self.mainlayout.addWidget(self.label)
        self.setLayout(self.mainlayout)
        self.thread1 = MyCameraThread1(camera_object=self.capture, parent=self)  # The index of camera should be given carefully.
        self.thread1.update.connect(self.refresh)
        self.thread1.start()


    def refresh(self, img):
        self.label.setPixmap(QPixmap.fromImage(img))  # the type of img is QImage

    def closeEvent(self, event):
        self.thread1.status = False  # this thread is not used in the payment system (the main process).



if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    app = QApplication(sys.argv)
    mywindow = CameraDialog(camera_object=cap)
    mywindow.show()
    try:
        sys.exit(app.exec_())
    except BaseException:
        cap.release()

