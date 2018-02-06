"""
Customisized QWidget
author = hobin
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys


class StandbyLayout(QWidget):
    """
    switching pictures every second
    """
    def __init__(self, parent=None):
        super(StandbyLayout, self).__init__(parent)
        self.time = 2500 # the time that every picture stands (ms)
        #  ---------------------------------------------------------------------
        self.pic1 = QPixmap()
        self.pic1.load('.\\Images\\a4.png')
        # self.pic1.scaled(400, 400, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.label1 = QLabel()
        self.label1.setPixmap(self.pic1)


        self.pic2 = QPixmap()
        self.pic2.load('.\\Images\\a5.png')
        self.label2 = QLabel()
        self.label2.setPixmap(self.pic2)


        self.pic3 = QPixmap()
        self.pic3.load('.\\Images\\a6.png')
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