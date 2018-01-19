"""

"""
import cv2
from PyQt5.QtCore import QSizeF, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QLabel, QGraphicsScene
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
        self.img = QImage()
        self.capture0 = cv2.VideoCapture(0)
        self.capture0.set(3, 600)  # 3 indicates the width;
        self.capture0.set(4, 800)  # 4 indicates the height;
        self.thread1 = MyCameraThread1(camera_object=self.capture0, parent=self) # The index of camera should be given carefully.
        self.thread1.update.connect(self.refresh)
        self.thread1.start()

    def refresh(self, img):
        self.setPixmap(QPixmap.fromImage(img)) # the type of img is QImage





