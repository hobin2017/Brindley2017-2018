"""
Media player
author = hobin;
email = '627227669@qq.com';
"""
import os
import sys
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


class MyMediaPlayer(QObject):

    def __init__(self, parent=None):
        super(MyMediaPlayer, self).__init__(parent)
        self.parent = parent
        dir_path = os.path.dirname(__file__)
        audio_path = os.path.join(dir_path, 'audio')
        file1_path = os.path.join(audio_path, 'Welcome.wav')
        file2_path = os.path.join(audio_path, 'openDoor.wav')
        file3_path = os.path.join(audio_path, 'payok.wav')
        file4_path = os.path.join(audio_path, 'payfail.wav')
        file5_path = os.path.join(audio_path, 'noGoodsOut.wav')
        file6_path = os.path.join(audio_path, 'Waiting.wav')
        file7_path = os.path.join(audio_path, 'noPay.wav')
        file8_path = os.path.join(audio_path, 'new_user_scan_code.wav')
        file9_path = os.path.join(audio_path, 'item_excess.wav')
        file10_path = os.path.join(audio_path, 'item_no_detection.wav')
        file11_path = os.path.join(audio_path, 'order_success.wav')
        file12_path = os.path.join(audio_path, 'no_user_detected.wav')
        file13_path = os.path.join(audio_path, 'multiple_user_detected.wav')
        file14_path = os.path.join(audio_path, 'order_change.wav')
        self.file01 = QMediaContent(QUrl.fromLocalFile(file1_path))  # you are welcome
        self.file02 = QMediaContent(QUrl.fromLocalFile(file2_path))  # Thank you for purchase
        self.file03 = QMediaContent(QUrl.fromLocalFile(file3_path))  # purchase successes
        self.file04 = QMediaContent(QUrl.fromLocalFile(file4_path))  # purchase fails
        self.file05 = QMediaContent(QUrl.fromLocalFile(file5_path))  # you are welcome for next time
        self.file06 = QMediaContent(QUrl.fromLocalFile(file6_path))  # we are checking, waiting for a while please
        self.file07 = QMediaContent(QUrl.fromLocalFile(file7_path))  # you have something unpaid
        self.file08 = QMediaContent(QUrl.fromLocalFile(file8_path))
        self.file09 = QMediaContent(QUrl.fromLocalFile(file9_path))
        self.file10 = QMediaContent(QUrl.fromLocalFile(file10_path))
        self.file11 = QMediaContent(QUrl.fromLocalFile(file11_path))
        self.file12 = QMediaContent(QUrl.fromLocalFile(file12_path))
        self.file13 = QMediaContent(QUrl.fromLocalFile(file13_path))
        self.file14 = QMediaContent(QUrl.fromLocalFile(file14_path))
        self.player = QMediaPlayer(self)
        self.player.setVolume(70)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.a = MyMediaPlayer()
        self.button01 = QPushButton('Play')
        self.button01.clicked.connect(self.play01)
        self.setCentralWidget(self.button01)

    def play01(self):
        self.a.player.setMedia(self.a.file05)
        self.a.player.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

