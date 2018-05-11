# PaymentSystem2017
Compared with the last version, the changes are listed below:
1. adding self.order_link which is used in the QR code;
2. adding self.transaction_not_end_status which is used to prevent self.timer1.start() somewhere;
3. ;
11. using QMeidaPlayer.mediaStatus() before QMeidaPlayer.play() to avoid the restart of the same media content;
