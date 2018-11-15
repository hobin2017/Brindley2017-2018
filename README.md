# PaymentSystem2017
Compared with Klas_V1_1_3, the changes in Klas_V1_1_4 are listed below:
1. use QTimer self.timer3 to show the pay successes view despite the failure of eliminating magnetic;
2. deleting the initialization of self.pay_clear_by_gesture in work3;
3. In work11_klas & work25, 3 actions are added: sending extra elimination command, starting self.timer3, re-initializing three status: self.timer3_not_timeout_status, self.manetic_signal_not_received and self.pay_clear_by_gesture;
4. In work24, using two status, self.timer3_not_timeout_status, self.manetic_signal_not_received, to ensure that the PaySuccess view is shown only once;

Compared with Klas_V1_1_4, the changes in Klas_V1_1_5 are listed below:
1. introducing the Ask4PaymentResultThread to ask the server for the payment result;
2. using new GesturePayThread (MyThread7_1_2) to start Ask4PaymentResultThread (work30) after posting the gesture-pay to server; 
3, adding 'error' singal and emitting it in the run function of the websocket thread (MyThread8_1_klas) since the third-party package 'SocketIO-client' might raise error. This also results in the error10 function to restart the MyThread8_1_klas;
