# PaymentSystem2017
Compared with the last version, the changes are listed below:
#1, Imgae-upload thread is added to upload three imgaes: user image, items image and thumbs-up image;
#2, fixing one bug: the account thread is not guaranteed to restart when both face detection and eye detection fails at first time. The situation is that the account thread is very close to end and the 'success' signal is emitted (At this time, account thread is stopped by the main process(account thread still is running) and the user-tracking thread starts. If the user-tracking thread cannot detect face and eyes, it will result in the restart of the account thread. However, the account thread is still running and hence the restart does not work as we expect.);
#3, all print statements are backup in loggers;
