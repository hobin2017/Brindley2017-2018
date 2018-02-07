"""
Loading the gif in QLabel;
Displaying an QLabel on another QLabel;
"""

import sys

from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.pixmap01 = QPixmap('.\\images\\linchao.jpg')
        self.label01 = QLabel(self)
        self.label01.setPixmap(self.pixmap01)
        # self.label01.setWindowOpacity(0.0)

        self.pixmap02 = QPixmap('.\\images\\whiteHand.png')
        self.movie = QMovie('.\\images\\handpay3.gif')
        self.label02 = QLabel()
        # self.label02.setPixmap(self.pixmap02)
        self.label02.setMovie(self.movie)
        self.movie.start()


        self.layout01 = QVBoxLayout()
        self.layout01.setAlignment(Qt.AlignRight)
        self.layout01.addWidget(self.label02)
        self.label01.setLayout(self.layout01)
        # self.label02.setVisible(False)
        self.setCentralWidget(self.label01)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())
