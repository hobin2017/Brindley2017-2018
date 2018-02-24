# PaymentSystem2017
Compared with the last version, the changes are listed below:
#1, Finding an error in the GestureThread since the data type of self.dict02['code'] is int not str!
#2, After the thumbs-up-detecting thread successes to detect the thumbs-up, a QLabel with gif is shown to interact with user. Currently, this gif is shown after the user is detected and this gif stops after the successful detection of thumbs-up;
#3, Introducing the socketClient thread which sends data to my server to indicate that the machine is alive, receives the data from my server to open door and receives the data from my server to confirm that the order is paid by QR code or gesture method;
#4, Adding two QLabels to show the end of the transaction;
#5, The audio file (*.wav) will be added after the successful pay for products;
#6, If the account does not give the access to us for automatic pay, the payment system does not show another image to cover the camera QLabel;
#7, The camera QLabel shows the mirror of the original frame by using the mirrored() of the QImage class;
