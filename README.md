# PaymentSystem2017
Compared with the PaymentSystem_V1_5_0, the modification for Brindley_V2_0_0 is listed below: 
1. the weigher module is firstly introduced to replece MyThread2_1 class (This will have effects in the place where self.thread2 and self.thread3 exist);
2. 'try..except' statements are added to the SQL thread (the MyThread3_2_1 class);
3. the verification of item weight is added after the SQL thread in work5 function. If the verification fails, one dialog (defined in DialogLayout.py file) will show until the verification successes;
4. commenting the useless usage QThread.setPriority();
5. the self-checking is firstly introduced into Brindley;
6. fixing one bug: the weigher detects zero and it refreshs the ShoppingList Layout (it does not refresh the last_result of the ML Model). What if customer place the same item into the weigher? Answer: the weigher sends signal to ML Model to detect items, and then the detected result is the same as the last result. Hence, the the ShoppingList still is empty! Solution: refreshing the value of last_result of the ML Model in work4b function. 
7. User guide is firstly introduced;
8. Reminder of Weight is firstly introduced;
 
