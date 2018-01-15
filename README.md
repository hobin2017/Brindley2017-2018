# PaymentSystem2017
Compared with version, the changes are listed below:
#1, using __slots__ to save the memory of a class(you can use sys.getsizeof() to know how many memories are used). However, this method has no effect in my code;
#2, using the set() function of VideoCapture to make the frame in fixed size (width= 640, height=800);
#3, the initialization will cause the initialization of the ML model and the ML model is initialized by using the subprocess;
#4, changing the MyCameraThread1 and MyThread2 class since the QThread might not release the camera after its run(). In addition, the run function of QThread can be recalled by using its start(); 
#5, 
