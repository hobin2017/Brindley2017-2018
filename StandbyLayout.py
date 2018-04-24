"""
Customisized QWidget
author = hobin;
email = '627227669@qq.com';
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os

class StandbyLayout(QWidget):
    """
    switching pictures every second
    """
    def __init__(self, parent=None):
        super(StandbyLayout, self).__init__(parent)
        dir_path = os.path.dirname(__file__)
        image_path = os.path.join(dir_path, 'Images')
        pic_path1 = os.path.join(image_path, 'page01.png')
        pic_path2 = os.path.join(image_path, 'page02.png')
        pic_path3 = os.path.join(image_path, 'page03.png')

        self.time = 2500 # the time that every picture stands (ms)
        #  ---------------------------------------------------------------------
        self.pic1 = QPixmap()
        self.pic1.load(pic_path1)
        # self.pic1.scaled(400, 400, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.label1 = QLabel()
        self.label1.setPixmap(self.pic1)


        self.pic2 = QPixmap()
        self.pic2.load(pic_path2)
        self.label2 = QLabel()
        self.label2.setPixmap(self.pic2)


        self.pic3 = QPixmap()
        self.pic3.load(pic_path3)
        self.label3 = QLabel()
        self.label3.setPixmap(self.pic3)

        #---------------------------------------------------------------------
        self.mainlayout = QStackedLayout()
        self.mainlayout.addWidget(self.label1)
        self.mainlayout.addWidget(self.label2)
        self.mainlayout.addWidget(self.label3)
        self.mainlayout.setCurrentWidget(self.label1)
        self.setLayout(self.mainlayout)

        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.switchPicture1)
        self.timer1.start(self.time)  # unit is 'ms'

        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.switchPicture2)

        self.timer3 = QTimer()
        self.timer3.timeout.connect(self.switchPicture3)


    def switchPicture1(self):
        self.timer1.stop()
        self.mainlayout.setCurrentWidget(self.label1)
        self.timer2.start(self.time)


    def switchPicture2(self):
        self.timer2.stop()
        self.mainlayout.setCurrentWidget(self.label2)
        self.timer3.start(self.time)

    def switchPicture3(self):
        self.timer3.stop()
        self.mainlayout.setCurrentWidget(self.label3)
        self.timer1.start(self.time)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = StandbyLayout()
    mainwindow.show()
    sys.exit(app.exec_())