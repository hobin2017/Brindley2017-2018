"""
Payment System
author = hobin
version = 1.0.2
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QStackedLayout
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
import qtmodern.styles
import qtmodern.windows
import sys


class PaymentSystem(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Payment System')
        self.main_widget = MainLayout(self)
        self.stand_by_widget = StandbyLayout(self)
        self.setCentralWidget(self.stand_by_widget)
        self.showFullScreen() # no Min Button and no Max Button
        self.main_widget.mainlayout.leftlayout.secondlayout.sendList.connect(self.main_widget.renewSum)
        self.test1()

    def closeEvent(self, event):
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.capture.release()
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.quit() # The first way to stop the thread.
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread

    def test1(self):
        product1 = ['tea康师傅冰红茶', '300ml', 5.5]
        product2 = ['tea', '400ml', 6]
        product3 = ['tea', '500ml', 7]
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3])
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3, product3])

    def mousePressEvent(self, event):
        """
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        :param event:
        :return:
        """
        self.setCentralWidget(self.main_widget)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = PaymentSystem()
    #mainwindow.show()
    # ----------using qtmordern ------------------------------
    qtmodern.styles.dark(app)
    mywindow = qtmodern.windows.ModernWindow(mainwindow)
    mywindow.show()
    # ----------------------------------------------------------------------
    sys.exit(app.exec_())
