"""
Media player
"""

from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class MyMediaPlayer(QObject):

    def __init__(self, parent=None):
        super(MyMediaPlayer, self).__init__(parent)
        self.parent = parent
        self.file01 = QMediaContent(QUrl.fromLocalFile('./audio/Welcome.wav'))  # you are welcome
        self.file02 = QMediaContent(QUrl.fromLocalFile('./audio/openDoor.wav'))  # Thank you for purchase
        self.file03 = QMediaContent(QUrl.fromLocalFile('./audio/payok.wav'))  # purchase successes
        self.file04 = QMediaContent(QUrl.fromLocalFile('./audio/payfail.wav'))  # purchase fails
        self.file05 = QMediaContent(QUrl.fromLocalFile('./audio/noGoodsOut.wav'))  # you are welcome for next time
        self.file06 = QMediaContent(QUrl.fromLocalFile('./audio/Waiting.wav'))  # we are checking, waiting for a while please
        self.file07 = QMediaContent(QUrl.fromLocalFile('./audio/noPay.wav'))  # you have something unpaid
        self.player = QMediaPlayer(self)
        self.player.setVolume(70)


