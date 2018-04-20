# -*- coding: utf-8 -*-
"""

"""
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QPushButton, QLabel, QMessageBox, QWidget, QHBoxLayout


class ReminderWeight01(QMessageBox):
    """
    QMessageBox is the subclass of the QDialog;
    QMessageBox class is supposed to be used with exec() function. Hence, it should have modality.
    the close function of the QMessageBox class seems useless at this case.
    """
    def __init__(self, parent=None):
        super(ReminderWeight01, self).__init__(parent)
        # parent_rect = parent.frameGeometry()  # The result is like PyQt5.QtCore.QRect(0, 0, 639, 479)
        # print(parent_rect)
        # self.width = int(parent_rect.width()/3)
        # self.height = int(parent_rect.height()/3)
        # self.x = int(parent_rect.width()/3)
        # self.y = int(parent_rect.height()/3)
        self.width = 500
        self.height = 500
        self.x = 700
        self.y = 300
        # these functions come from QWidget
        self.setFixedSize(self.width, self.height)
        self.move(self.x, self.y)
        self.setText("Sorry, I can't see clearly. please arrange them again.")
        self.setStyleSheet('color: rgb(255,255,255); background-color: rgb(64,64,64);')
        self.setStandardButtons(QMessageBox.NoButton)
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlags(Qt.SplashScreen)  # This should be executed after the setWindowModality() function;




class ReminderWeight02(QDialog):

    def __init__(self, parent=None):
        super(ReminderWeight02, self).__init__(parent)
        # parent_rect = parent.frameGeometry()  # The result is like PyQt5.QtCore.QRect(0, 0, 639, 479)
        # print(parent_rect)
        # print(parent.x(), parent.y(), parent.width(),parent.height())
        # self.width = int(parent_rect.width()/3)
        # self.height = int(parent_rect.height()/3)
        # self.x = int(parent_rect.width()/3)
        # self.y = int(parent_rect.height()/3)

        self.width = 500
        self.height = 300
        self.x = 700
        self.y = 300
        # these functions come from QWidget
        self.setFixedSize(self.width, self.height)
        self.move(self.x, self.y)
        self.setStyleSheet('background-color: rgb(64,64,64);')
        self.setWindowFlags(Qt.SplashScreen)
        # self.setWindowFlags(Qt.FramelessWindowHint|Qt.CustomizeWindowHint)

        #layout management
        self.mainlayout = QHBoxLayout()
        self.setLayout(self.mainlayout)
        self.label1 = QLabel("Sorry, I can't see them clearly. please arrange them again.")
        # self.label1.setScaledContents(True)  # useless
        # self.label1.adjustSize()
        self.label1.setWordWrap(True)
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setStyleSheet('color: rgb(255, 255, 255); font: 14pt;')
        self.mainlayout.addWidget(self.label1)





class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.a = ReminderWeight02(self)
        self.main1 = QWidget()
        self.layout = QHBoxLayout()
        self.button1 = QPushButton('show dialog')
        self.button1.clicked.connect(self.work1)
        self.button2 = QPushButton('close dialog')
        self.button2.clicked.connect(self.work2)
        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)
        self.main1.setLayout(self.layout)
        # self.showMaximized()
        self.setCentralWidget(self.main1)

    def work1(self):
        # self.a.show()
        self.a.setVisible(True)

    def work2(self):
        # self.a.close()  # This does not work for the QMessageBox class.
        self.a.setHidden(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

