"""
Using QThread to perform the time-consuming task.
"""
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import time
import cv2


class MyCameraThread1(QThread):
    """
    It returns a QImage object for QLabel displaying it;
    """
    update = pyqtSignal(object)

    def __init__(self, camera_object, parent=None):
        super(MyCameraThread1, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = camera_object


    def run(self):
        self.status = True  # It is for calling of start() again.
        while self.status:
            ret, img1 = self.capture.read()
            img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
            height, width, channel = img2.shape  # width=640, height=480
            bytes_per_line = 3 * width
            img3 = QImage(img2.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.update.emit(img3)
            time.sleep(0.1)


class MyThread2(QThread):
    """
    This is used for detecting the products;
    """
    detected = pyqtSignal()

    def __init__(self, camera_object, parent=None):
        super(MyThread2, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = camera_object


    def run(self):
        self.status = True
        try:
            while self.status:
                ret, img1 = self.capture.read()
                img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                time.sleep(0.3)
                ret, img2 = self.capture.read()
                img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                img3 = cv2.absdiff(img1_gray, img2_gray)
                img3_1 = cv2.GaussianBlur(img3, (3, 3), 0, 0)
                thresh, img3_2 = cv2.threshold(src=img3_1, thresh=34, maxval=255, type=cv2.THRESH_BINARY)
                element1 = cv2.getStructuringElement(0, (3, 3))
                img3_3 = cv2.dilate(img3_2, kernel=element1)
                full_nums = img3_3.size
                nums_detect = img3_3.sum() / 255.0
                rate_detect = nums_detect / full_nums
                if rate_detect > 0.1:
                    self.detected.emit()
                    time.sleep(1)
        except BaseException:
            self.capture.release()
            self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.capture.release()


if __name__ == '__main__':
    print(sys.getsizeof(MyCameraThread1))
