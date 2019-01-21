# -*- coding: utf-8 -*-
"""
By using QApplication.processEvents, a QWidget appears immediately before a time-consuming operation.
"""
import sys

import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QLabel, QApplication


class LoadingLayout01(QFrame):

    def __init__(self):
        super().__init__(flags=Qt.FramelessWindowHint)
        self.setFixedSize(1920, 1080)
        self.setStyleSheet('background:yellow;')
        self.loading_pixmap = QPixmap('./Images/Loading_page.jpg')
        self.loading_widget = QLabel(self)
        self.loading_widget.setPixmap(self.loading_pixmap)
        self.loading_widget.setScaledContents(True)

        # layout management
        self.loading_widget.move(0, 0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = QLabel()
    a.setStyleSheet('background: yellow;')
    a.setFixedSize(1920, 1080)
    a.show()
    app.processEvents()  # to show the widget immediately
    time.sleep(3)  # the time consumed by creating all other things for the main process
    mywidget = LoadingLayout01()
    mywidget.show()
    a.close()
    # mywidget.showFullScreen()
    sys.exit(app.exec_())

