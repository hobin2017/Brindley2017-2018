"""
Aim: to display the image(jpg) which is binary data in QLabel;
"""
import requests
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.label1 = QLabel()
        resp = requests.get('https://wx.qlogo.cn/mmopen/vi_32/yDFJbcnUg9OFKoouQyrPAuUUtsGaAUC4ShrPrZvUNTWQdqjXwoDyjw81TTcpCkWHt4ibOr1SAsUINGicUZYzfLIw/0')
        self.pixmap01 = QPixmap()
        # the resp.content is the binary data which represents the jpg image
        self.pixmap01.loadFromData(resp.content)
        self.label1.setPixmap(self.pixmap01)
        self.setCentralWidget(self.label1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

