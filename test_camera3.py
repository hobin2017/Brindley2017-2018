"""
1, using QLabel to display a frame frequently;
2, using OpenCV to initiate the camera;
3, using QThread to initiate the refresh of QLabel;
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import cv2
import time

class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.resize(550, 550)
        self.setWindowTitle('vedio control')
        self.status = 0  # 0 is init status;1 is play video; 2 is capture video
        self.image = QImage()

        self.playcapture = cv2.VideoCapture(0)
        startbtn = QPushButton('start')
        startbtn.clicked.connect(self.start1)
        stopbtn = QPushButton('Stop')
        stopbtn.clicked.connect(self.stop1)
        vbox = QVBoxLayout()
        vbox.addWidget(startbtn)
        vbox.addWidget(stopbtn)
        self.piclabel = QLabel('pic')
        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addStretch(1)
        hbox.addWidget(self.piclabel)
        self.setLayout(hbox)

        self.playtimer = Timer()
        self.playtimer.updateTime.connect(self.PlayVideo)

    def PlayVideo(self):
        ret, im = self.playcapture.read() # the data type is uint8.
        #cv2.cvtColor(im, im, cv2.COLOR_BGR2RGB) #the return value of read is not allowed to change?
        # ----- converting the data structure of OpenCV to the data structure of QImage ------------
        height, width, channel = im.shape
        bytesPerLine = 3 * width
        self.image = QImage(im.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.image = self.image.rgbSwapped() # the order of OpenCV is BGR and the order of QImage is BGR.
        # ------------------------------------------------------------------------------------------
        self.piclabel.setPixmap(QPixmap.fromImage(self.image))

    def start1(self):
        self.playtimer.start()
        
    def stop1(self):
        self.playtimer.stop()


class Timer(QThread):
    updateTime = pyqtSignal()
    def __init__(self,parent=None):
        super(Timer, self).__init__(parent)
        self.stoped = False
        # The purpose of a QMutex is to protect an object, data structure or section of code so that only one thread can access it at a time
        self.mutex = QMutex() # at this time, it is useless.

    def run(self):
        with QMutexLocker(self.mutex):
            self.stoped = False

        while True:
            if self.stoped:
                return
            self.updateTime.emit()
            time.sleep(0.1)

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stoped = True

    def isStoped(self):
        with QMutexLocker(self.mutex):
            return self.stoped


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
