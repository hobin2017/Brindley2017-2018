# PaymentSystem2017
Compared with the last version, the changes are listed below:
#1, the weigher module is firstly introduced to replece MyThread2_1 class (This will have effects in the place where self.thread2 and self.thread3 exist);
#2, 'try..except' statements are added to the SQL thread (the MyThread3_2_1 class);
#3， the verification of item weight is added after the SQL thread in work5 function. If the verification fails, one dialog (defined in DialogLayout.py file) will show until the verification successes;
#4, my customized QDialog class is introduced in the ShoppingList.py to give a message to customer;
#5, commenting the useless usage QThread.setPriority();
#6, adding the self-checking is firstly introduced into Brindley;
#7， finding one bug caused by the cooperation of the Weigher and the ML Model: the weigher detects zero and it refreshs the ShoppingList Layout (it does not refresh the last_result of the ML Model). What if customer place the same item into the weigher? Ans: the weigher sends signal to ML Model to detect items, and then the detected result is the same as the last result. Hence, the the ShoppingList still is empty!

 
