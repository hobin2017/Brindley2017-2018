# PaymentSystem2017
Compared with Klas_V1_1_4, the changes in Klas_V1_1_5 are listed below:
1. introducing the Ask4PaymentResultThread to ask the server for the payment result;
2. adding 'error' singal and emitting it in the run function of the websocket thread (MyThread8_1_klas) since the third-party package 'SocketIO-client' might raise error. This also results in the error10 function to restart the MyThread8_1_klas;

