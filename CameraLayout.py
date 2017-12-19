from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class CameraWidget(QGraphicsView):
    """
    QGraphicsView uses QGraphicsScene by 'setScene';
    QGraphicsScene uses QGraphicsVideoItem by 'addItem';
    QGraphicsVideoItem is also used by QCamera according to 'setViewfinder';
    """
    def __init__(self, parent=None):
        super(CameraWidget, self).__init__(parent)

        size_info = self.geometry() # QRect class
        self.x = size_info.x()
        self.y = size_info.y()
        self.width = size_info.width()
        self.height = size_info.height()
        self.scene = QGraphicsScene(self.x, self.y, self.width, self.height)
        self.setScene(self.scene)  # to visualize the QGraphicsScene
        self.videoItem1 = QGraphicsVideoItem()  # QGraphicsVideoItem actually is a subclass of the QGraphicsItem class
        self.videoItem1.setSize(QSizeF(self.width, self.height))  # QGraphicsVideoItem will draw video scaled to fit size according to its fillMode.
        self.videoItem1.setPos(self.x, self.y)  # the setPos() function can be checked in QGraphicsItem class.
        self.scene.addItem(self.videoItem1)  # QGraphicsScene can add your existing QGraphicsItem objects by calling addItem()
        # QCamera can be used with QCameraViewfinder for viewfinder display, QMediaRecorder for video recording and QCameraImageCapture for image taking.
        self.camera1 = QCamera(QCameraInfo.defaultCamera(), self)
        self.camera1.setViewfinder(self.videoItem1)  # The parameter could be QVideoWidget, QGraphicsVideoItem and QAbstractVideoSurface.
        # The capture mode only could be QCamera.CaptureViewfinder, CaptureStillImage and CaptureVideo.
        #self.camera1.setCaptureMode(QCamera.CaptureVideo)
        self.camera1.setCaptureMode(QCamera.CaptureViewfinder)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # do not show horizontal scroll bar.

    def mousePressEvent(self, event):
        self.camera1.start()




