# PaymentSystem2017
1. Klas with version 0.0.0, basically is the same as the Brindley_V2_0_0 but it changes the function name by appending corresonding thread name. for example, work2() becomes ml_item_work2. (Not sure that it is exactly the same as the Brindely_V2_0_0 file.)
2. Klas with version 1.0.0, changes its logical part to finish the gesture pay.
3. Compared with the version 1.0.0, Klas with version 1.1.0 modifies the cooperation between account thread and the ml gesture model. In other words, the account thread uses the frame provided by the ml gesture model. Another difference is that self.wave_status is added to weigher module (Weigher2_1).
4. Compared with the version 1.1.0, Klas with version 1.1.1 uses only one weigher class by exploiting the signal disconnection.
- QTimer.setSingleShot(True) for self.timer1;
- showing the correspoding image evern there is the wrong verification (Compared with the last version, Klas just clear the layout)l
- fixing bug for selfCheck.py and Weigher.py. the main problem is the data conversion and current solution is the canReadLine() before using QSerialPort.readLine();
- connecting error signals of threads;
- dealing with error: retry 2 or 3 times;
- better shopping_timer_work3_klas: clearing the frame of ml gesture model and account thread, try...except statement for disconnection of readyRead signal of QSerialPort; 
- the 'Connection' header of request changes from 'keep-alive' to 'close';
- the cooperation between Klas and account: the ml gesture model does not rework after the account thread detects no user. The reason is there is no while loop in this account thread;

