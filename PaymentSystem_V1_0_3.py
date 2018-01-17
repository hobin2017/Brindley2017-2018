"""
Payment System
author = hobin
version = 1.0.3
"""

import cv2
import qtmodern.styles
import qtmodern.windows
import sys
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedLayout
# -----------------------------------------------------------------------------------------------
from MainLayout import MainLayout
from StandbyLayout import StandbyLayout
from CameraThread import MyThread2
from ML_Model import Detection1



class PaymentSystem(QMainWindow):
    global app  # the QApplication

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
        self.showFullScreen() # no Min Button and no Max Button in the main layout
        self.main_widget.mainlayout.leftlayout.secondlayout.sendList.connect(self.main_widget.renewSum)


        # for switching the standby layout and main layout;
        self.capture1 = cv2.VideoCapture(1)
        self.capture1.set(3, 640)  # 3 indicates the width;
        self.capture1.set(4, 800)  # 4 indicates the height;
        self.thread2 = MyThread2(camera_object=self.capture1, parent=self)
        self.thread2.detected.connect(self.work1)
        self.thread2.start()

        # for work3
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.work3)


        # ML Model
        #  it's start() is used in work1();
        self.thread3 = Detection1(camera_object=self.capture1, parent=self)
        self.thread3.detected.connect(self.work2)


    def work1(self):
        """
        Aim: switching the layout from standby to main;
        Requirement:
        stopping the CameraThread and starting the timer
        Optimization:
        when detecting the products, we can switch off the QTimer of StandbyLayout.
        But you don't know which one is working.
        """
        self.thread2.quit()  # I guess, it does not release the camera.
        self.main_frame.stacked_layout.setCurrentWidget(self.main_widget)
        self.timer1.start(60000)  # for switching back to the standby layout;
        self.work4()


    def work2(self, result_detected):
        """
        Aim: to display the result of the detection;
        :param result_detected: a list;
        :return: a list of detected product;
        """
        print(result_detected)
        product1 = ['tea康师傅冰红茶', '300ml', 5.5]
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product1])


    def work3(self):
        """
        when there is no action, returns to the standby layout;
        """
        self.timer1.stop()
        self.main_frame.stacked_layout.setCurrentWidget(self.stand_by_widget)
        time.sleep(1)
        # If the thread does not stop yet(still staying in the its run) and you call its start(), this start will be ignored;
        self.thread2.start()  # Ideally, this is not the first time to starting this thread! It is a re-start!


    def work4(self):
        """
        The strategy for detecting the products
        :return:
        """
        for i in range(10):
            self.thread3.start()
            while self.thread3.isRunning():
                app.processEvents()


    def closeEvent(self, event):
        # self.main_widget.mainlayout.rightlayout.secondlayout.thread1.quit() # The first way to stop the thread.
        self.main_widget.mainlayout.rightlayout.secondlayout.thread1.status = False  # The second way to stop the thread
        self.thread2.quit()
        self.main_widget.mainlayout.rightlayout.secondlayout.capture0.release()
        self.capture1.release()


    def test1(self):
        """It will be redundant since the detection model is introduced;"""
        product1 = ['tea康师傅冰红茶', '300ml', 5.5]
        product2 = ['tea', '400ml', 6]
        product3 = ['tea', '500ml', 7]
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3])
        self.main_widget.mainlayout.leftlayout.secondlayout.displayProduct([product1, product2, product3, product3])



if __name__ == '__main__':
    global app
    app = QApplication(sys.argv)
    mainwindow = PaymentSystem()
    # ----------using qtmordern ------------------------------
    qtmodern.styles.dark(app)
    mywindow = qtmodern.windows.ModernWindow(mainwindow)
    mywindow.show()
    # ----------------------------------------------------------------------
    # mainwindow.show()
    sys.exit(app.exec_())

