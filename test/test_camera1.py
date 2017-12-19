"""
Python = 3.6
Qt = 5.6
aim: using multiple camera
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class Camera(QMainWindow):

    def __init__(self, parent=None):
        super(Camera, self).__init__(parent)
        size_info = self.geometry()
        self.x = size_info.x()
        self.y = size_info.y()
        self.width = size_info.width()
        self.height = size_info.height()
        # QGraphicsScene only manages the items. You need to create a QGraphicsView widget to visualize the scene.
        self.scene = QGraphicsScene(self.x, self.y, self.width, self.height)
        self.videoItem1 = QGraphicsVideoItem()  # QGraphicsVideoItem actually is a subclass of the QGraphicsItem class
        self.videoItem1.setSize(QSizeF(self.width, self.height))  # QGraphicsVideoItem will draw video scaled to fit size according to its fillMode.
        self.videoItem1.setPos(self.x, self.y) # the setPos() function can be checked in QGraphicsItem class.
        self.scene.addItem(self.videoItem1) # QGraphicsScene can add your existing QGraphicsItem objects by calling addItem()
        # QCamera can be used with QCameraViewfinder for viewfinder display, QMediaRecorder for video recording and QCameraImageCapture for image taking.
        self.camera1 = QCamera(QCameraInfo.availableCameras()[0], self)
        self.camera1.setViewfinder(self.videoItem1) # The parameter could be QVideoWidget, QGraphicsVideoItem and QAbstractVideoSurface.
        # The capture mode only could be QCamera.CaptureViewfinder, CaptureStillImage and CaptureVideo.
        self.camera1.setCaptureMode(QCamera.CaptureVideo)

        # self.camera2 = QCamera(QCameraInfo.availableCameras()[1], self)
        # self.videoItem2 = QGraphicsVideoItem()
        # self.camera2.setViewfinder(self.videoItem2)
        # self.videoItem2.setSize(QSizeF(500, 500))
        # self.videoItem2.setPos(500, 0)
        # self.camera2.setCaptureMode(QCamera.CaptureVideo)
        # self.scene.addItem(self.videoItem2)

        # self.camera3 = QCamera(QCameraInfo.availableCameras()[2], self)
        # self.videoItem3 = QGraphicsVideoItem()
        # self.camera3.setViewfinder(self.videoItem3)
        # self.videoItem3.setSize(QSizeF(500, 500))
        # self.videoItem3.setPos(0, 500)
        # self.camera3.setCaptureMode(QCamera.CaptureVideo)
        # self.scene.addItem(self.videoItem3)


        self.view = QGraphicsView() # QGraphicsView is a subclass of QWidget class
        self.view.setScene(self.scene) # to visualize the QGraphicsScene
        self.setCentralWidget(self.view)


    def mousePressEvent(self, event):
        self.camera1.error.connect(self.test1) # it seems useless.
        # The state of QCamera only could be QCamera.UnloadedState, LoadedState and ActiveState.
        # The success of starting can be detected by QCamera status (8 means success).
        self.camera1.start() # changing the state of QCamera to QCamera.ActiveState.
        #self.camera2.start()
        #self.camera3.start()

    def test1(self):
        print('There is an error')





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    camera = Camera()
    camera.show()
    sys.exit(app.exec_())



