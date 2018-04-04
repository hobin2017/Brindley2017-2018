"""
Media player
"""
import os
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


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
        self.file01 = QMediaContent(QUrl.fromLocalFile(file1_path))  # you are welcome
        self.file02 = QMediaContent(QUrl.fromLocalFile(file2_path))  # Thank you for purchase
        self.file03 = QMediaContent(QUrl.fromLocalFile(file3_path))  # purchase successes
        self.file04 = QMediaContent(QUrl.fromLocalFile(file4_path))  # purchase fails
        self.file05 = QMediaContent(QUrl.fromLocalFile(file5_path))  # you are welcome for next time
        self.file06 = QMediaContent(QUrl.fromLocalFile(file6_path))  # we are checking, waiting for a while please
        self.file07 = QMediaContent(QUrl.fromLocalFile(file7_path))  # you have something unpaid
        self.player = QMediaPlayer(self)
        self.player.setVolume(70)


