# PaymentSystem2017
Compared with the last version, the changes are listed below:
1. using new GesturePay thread, MyThread7_1_1_klas_singtel;
2. GesturePay thread will record the success_number in work6;
3. disconnecting the 'payclear_success' signal of socketIO thread with work11 and instead connecting the 'order_success' singal of the GesturePay thread with work11; 
4. connecting the 'order_error' signal of the order thread with error07. This signal is emitted when the HTTP status code is not 200;
5. using local server instead of a server with public IP;
6. changing the url in the 'Klsa2_Singtel.cfg' file (the host name in url will be 127.0.0.1);
