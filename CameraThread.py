"""

"""
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import time
import cv2


class MyCameraThread1(QThread):
    """
    It returns a QImage object for QLabel displaying it;
    """
    update = pyqtSignal(object)

    def __init__(self, cam_num, parent=None):
        super(MyCameraThread1, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = cv2.VideoCapture(cam_num)

    def run(self):
        self.status = True  # It is for calling of start() again.
        while self.status:
            ret, img1 = self.capture.read()
            img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            height, width, channel = img2.shape  # width=640, height=480
            bytes_per_line = 3 * width
            img3 = QImage(img2.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.update.emit(img3)
            time.sleep(0.15)


class MyThread2(QThread):
    """
    This is used for detecting the products
    """
    update = pyqtSignal(object)

    def __init__(self, cam_num, parent=None):
        super(MyThread2, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = cv2.VideoCapture(cam_num)

    def run(self):
        pass
