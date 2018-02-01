# PaymentSystem2017
Compared with version, the changes are listed below: 
#1, the error information about the account thread can be catch by using traceback and sys modules; 
#2, the cooperation between user-tracking thread and accound thread; 
#3, the cooperation between user-tracking thread and thread1; 
#4, the account thread is not initiated by SQL thread and it begins independently; 
#5, the current structure of the account thread contains a while loop, the frame is refreshed inside the while loop and it stops itself inside the while loop;
#6, the current structure of the user-tracking thread contains a while loop, the frame is refreshed inside the while loop and it stops itself inside the while loop;
