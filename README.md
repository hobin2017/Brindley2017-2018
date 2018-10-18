# PaymentSystem2017
Compared with Klas_V1_1_4, the changes are listed below:
1. using new user interface for Singtel, and the camera thread for user is added back. What is more, item model and gesture model are changed as camera obejct changes;
2. AccountThread, QRcodeThread, GesturePayThread, ImageUploadThread are changes since the server requires additional parameters when doing the HTTP POST;
3. zeroing the weigher is first introduced into WebsocketClientThread (MyThread8_3);
4. new function 'getting_ip_address' to get the current ip;
5. new function 'loading_images2memory' to load the local images into a dict named by 'self.item_images_dict' in Klas_Singtel;
6. using the DoorController class to replace the SerialPortConsole class;
7. using skuDownloadThread and skuDownloadFinishedThread to replace the SkuSysnServer;
8. if a update occurs when Klas_Singtel is running, the dictionary 'self.item_images_dict' will be updated in work28;
9. adding QTimer 'self.databse_update_timer' to ask the server for latest information (work26). work26 will make work3 to start the skuDownloadThread01 to do the work;
10. using Weigher3_1 and Weigher3_2 to support g/kg operation;
11. deleting item quality thread;
12. new 'layout' keyword is added to the configuration file;
13. As the server requires the data about the 'weight', this data is given to QRcodeThread in work5;
14. reimplement the 'showHandgif' function;
15. In work27. Klas_Singtel informs the server which of items are update. The server only gives you 20 records at every update request;
16. using self.shopping_time_counter and self.accelerate_to_standby_counter in Klas_Singtel for easy modification;
17. Before initializing Klas_Singtel, a QLabel is shown;
18. stopping the camera thread and releasing the camera in the closeEvent function 
