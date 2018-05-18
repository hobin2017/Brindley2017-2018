# PaymentSystem2017
Compared with the last version, the changes are listed below:
1. adding self.order_link which is used in the QR code;
2. adding self.transaction_not_end_status which is used to prevent self.timer1.start() somewhere;
3. adding self.pay_clear_by_gesture which is set to False if the payment is finished by scanning the code (websocket_work25);
4. adding self.success_order_number which is provided by websocket and it is used for image-upload thread and item-quality thread;
5. self.timer1 will be restart 3 mins if there is a change in weight. self.timer1 will be restart 8 seconds if the weight is near zero;
6. the malware of order might happens and it is handled in account_work6_klas (whether self.order_number == self.thread0_0.order_number);
7. different process for the result of the account thread such as no-well matched user(account_work7_klas), no user face detected(account_work17_klas) and multiple user faces detected(account_work18_klas);
8. the door_controller module written by my workmate, is firstly introduced into Klas. One main important affect is that Klas is to eliminate the magnetic after receiving the pay clear signal from server （websocket_work11_klas and websocket_work25）. And only if the door controller receives the seccessful elinimation of magnetic signal, the pay success layout will be showed;
9. cam_path is firstly introduced into Klas;
10. adding self.failed_detection_local_counter since the no user face is detected forever (In fact, there is a user face but the light affects the algorithm). Currently, it is used to design whether to show the QR code or to restart the ml gesture thread;
11. using QMeidaPlayer.mediaStatus() before QMeidaPlayer.play() to avoid the restart of the same media content;
12. the sql thread establish the new connection to the database every time since there is a cache for every connection;
