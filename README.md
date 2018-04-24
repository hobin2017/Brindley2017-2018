# PaymentSystem2017
Compared with the last version, the changes are listed below:
1. using the Detection2_3_2 class to emit the frame and the gesture position after successful detection. Hence, the cooperation between Klas and the Detection2_3_2 class (ml_gesture_work10_klas02 function) is required which results the modification in ml_gesture_work10_klas02 function and account_work6_klas function. The account_work16_klas function is firstly introduced and executed by the 'freezing_gesture' signal of the MyThread4_0_1_1 class after account thread detects only one face;
2. using the MyThread4_0_1_2 class to emits the information about the user head rather than the information about the user face;
3. playing corresponding sound to remind user;
4. 'try...except' statements are used when trying to get the user portrait of the wechat account, the reason is that the network has great impact on access of the user wechat portrait. If it fails, the default user portrait is used (Using the MyThread4_0_1_3 class); 
