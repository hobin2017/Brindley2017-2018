"""
1, using QLabel to display a frame frequently;
2, using OpenCV to initiate the camera;
3, using app.processEvents to initiate the refresh of QLabel;
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import cv2

class MainWindow(QWidget):
    global app
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
        self.flag = False # True indicates that the loop is alive.


    def PlayVideo(self):
        while self.flag:
            ret, im = self.playcapture.read() # the data type is uint8.
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)  # the order of OpenCV is BGR and the order of QImage is BGR.
            # ----- converting the data structure of OpenCV to the data structure of QImage ------------
            height, width, channel = im.shape
            bytesPerLine = 3 * width
            self.image = QImage(im.data, width, height, bytesPerLine, QImage.Format_RGB888)
            #self.image = self.image.rgbSwapped() # the order of OpenCV is BGR and the order of QImage is BGR.
            # ------------------------------------------------------------------------------------------
            self.piclabel.setPixmap(QPixmap.fromImage(self.image))
            app.processEvents()

    def start1(self):
        self.flag = True
        self.PlayVideo()

    def stop1(self):
        self.flag = False

    



if __name__ == "__main__":
    global app
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
