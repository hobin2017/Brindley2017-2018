"""
author: hobin;
email = '627227669@qq.com';
"""
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication


class EndLayout(QLabel):

    def __init__(self,parent=None, img_path=None):
        super(EndLayout, self).__init__(parent)
        self.img = QPixmap(img_path)
        self.setPixmap(self.img)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.img = EndLayout(parent=self, img_path='.//Images//pay_success.png')
        self.setCentralWidget(self.img)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

