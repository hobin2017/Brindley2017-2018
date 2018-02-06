# PaymentSystem2017
Compared with the last version, the changes are listed below:
#1, introducing the thumbs-up-detecting thread;
#2, introducing the gesture-pay thread;
#3, the thumbs-up-detecting thread has a while loop, begins independently after thread2 and stops on its own;
#4, the gesture-pay thread starts after the successful detection of thumbs-up;
#5, using new_user_flag and new_order_flag in thumbs-up-deteting thread to allow the detection for thumbs-up;
#6, using two extra variable 'user_id' and 'order_number' in the PaymentSystem class to keep the user id and order number are updated;
 
