# PaymentSystem2017
Compared with the last version, the changes are listed below:
1. the signal connection is changed from the default type (Qt.AutoConnection) to Qt.QueuedConnection; By default, when a signal is emitted, the slots connected to it are usually executed immediately, just like a normal function call. The situation is slightly different when using queued connections; in such a case, the code following the emit keyword will continue immediately, and the slots will be executed later (The Qt Company). The article can be accessed in this [link](http://doc.qt.io/qt-5/signalsandslots.html);
2. using the Detection2_3_2 class to emit the frame and the gesture position after successful detection. Hence, the cooperation between Klas and the Detection2_3_2 class (ml_gesture_work10_klas02 function) is required which results the modification in ml_gesture_work10_klas02 function and account_work6_klas. 
3. ;
