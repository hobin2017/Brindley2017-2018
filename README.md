# PaymentSystem2017
Compared with the last version, the changes are listed below:
1. adding self.order_link which is used in the QR code;
2. adding self.transaction_not_end_status which is used to prevent self.timer1.start() somewhere;
3. adding self.pay_clear_by_gesture which is set to False if the payment is finished by scanning the code (websocket_work25);
4. adding self.success_order_number which is provided by websocket and it is used for image-upload thread and item-quality thread;
5. self.timer1 will be restart 3 mins if there is a change in weight;
6. self.timer1 will be restart 8 seconds if the weight is near 0;
7. different process for the result of the account thread such as no-well matched user(account_work7_klas), no user face detected(account_work17_klas) and multiple user faces detected(account_work18_klas);
11. using QMeidaPlayer.mediaStatus() before QMeidaPlayer.play() to avoid the restart of the same media content;
