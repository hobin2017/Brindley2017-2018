
"""
Payment System
author = hobin
version = 1.0.1
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from MainLayout import MainLayout
import qtmodern.styles
import qtmodern.windows
import sys

class PaymentSystem(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Payment System')
        self.mainWidget = MainLayout(self)
        self.setCentralWidget(self.mainWidget)
        #self.showFullScreen() # no Min Button and no Max Button
        self.mainWidget.mainlayout.leftlayout.secondlayout.sendList.connect(self.mainWidget.renewSum)
        self.test1()

    def test1(self):
        product1 = ['tea康师傅冰红茶', '300ml', 5.5]
        product2 = ['tea', '400ml', 6]
        product3 = ['tea', '500ml', 7]
        self.mainWidget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3])
        self.mainWidget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3, product3])





if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = PaymentSystem()
    mainwindow.show()
    # ----------using qtmordern ------------------------------
    # qtmodern.styles.dark(app)
    # mywindow = qtmodern.windows.ModernWindow(mainwindow)
    # mywindow.show()
    # ----------------------------------------------------------------------
    sys.exit(app.exec_())

