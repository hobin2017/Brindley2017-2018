"""
Payment System
author = hobin
version = 1.0.2
"""
import qtmodern.styles
import qtmodern.windows
import sys

import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
from CameraThread import MyThread2



class PaymentSystem(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Payment System')
        self.main_frame = QWidget()
        self.main_widget = MainLayout(self)
        self.stand_by_widget = StandbyLayout(self)
        self.main_frame.stacked_layout = QStackedLayout()
        self.main_frame.stacked_layout.addWidget(self.stand_by_widget)
        self.main_frame.stacked_layout.addWidget(self.main_widget)
        self.main_frame.setLayout(self.main_frame.stacked_layout)
        self.setCentralWidget(self.main_frame)
        self.showFullScreen() # no Min Button and no Max Button
        self.main_widget.mainlayout.leftlayout.secondlayout.sendList.connect(self.main_widget.renewSum)

        self.thread2 = MyThread2(cam_num=1, parent=self)
        self.thread2.detected.connect(self.work1)
        self.thread2.start()

        self.timer1 = QTimer(self) # for test2
        self.timer1.timeout.connect(self.test2)

        self.test1()

    def work1(self):
        """
        Requirement:
        stopping the CameraThread and starting the timer
        Optimization:
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        But you don't know which one is working.
        """
        self.thread2.quit()
        self.main_frame.stacked_layout.setCurrentWidget(self.main_widget)
        self.timer1.start(4000)



    def closeEvent(self, event):
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.quit() # The first way to stop the thread.
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread
        self.thread2.quit()
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.capture.release()
        self.thread2.capture.release()


    def test1(self):
        product1 = ['tea康师傅冰红茶', '300ml', 5.5]
        product2 = ['tea', '400ml', 6]
        product3 = ['tea', '500ml', 7]
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3])
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3, product3])

    def test2(self):
        """
        when there is no action, returns to the standby layout
        """
        self.timer1.stop()
        self.main_frame.stacked_layout.setCurrentWidget(self.stand_by_widget)
        time.sleep(1)
        self.thread2.start()





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
