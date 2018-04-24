"""
Smooth Face Tracking - Primary user tracking
The main idea is to compare the center point of the current user face with the prior center point;
It is a python version of this article (Synaptitude,2015) and the link is given below:
http://synaptitude.me/blog/smooth-face-tracking-using-opencv/

author = hobin;
email = '627227669@qq.com';
"""
import traceback
import logging
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import time
import cv2

class MyThread6(QThread):
    """
    This thread is used after the account thread.
    """
    tracking_failed = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread6, self).__init__(parent)
        self.parent = parent
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_eye.xml')
        self.priorCenter = [0,0]  # the position of the center point of the user face which is given by account thread;
        self.faceNotFound = True  # This means that there is no user detected in the last frame or the first time;
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.frame_width = 600  # It is currently specified manually and is the corresponding width of the camera width;
        self.frame_height = 450


    def run(self):
        img = cv2.cvtColor(self.frame, 0)
        gray_frame01 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_frame02 = cv2.equalizeHist(gray_frame01)  # attention one
        faces = self.face_cascade.detectMultiScale(gray_frame02, 1.1, 3, minSize=(30, 30))
        print('User tracking thread begins')
        # the largest face will be the first face detected because classifiers will search something called an image pyramid
        if len(faces) > 0:
            for index, (x, y, w, h) in enumerate(faces):
                currentCenter = [x + w // 2, y + h // 2]
                if self.faceNotFound:
                    self.priorCenter = currentCenter
                    self.faceNotFound = False  # This means that there is  user detected in the last frame;
                    print('User tracking thread with Face Detection (end): the first person detected by the algorithm becomes the primary user.')
                    break
                elif abs(currentCenter[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                        currentCenter[1] - self.priorCenter[1]) < self.frame_height // 6:
                    if abs(currentCenter[0] - self.priorCenter[0]) < 7 and abs(currentCenter[1] - self.priorCenter[1]) < 7:
                        currentCenter = self.priorCenter
                    currentCenter[0] = (currentCenter[0] + 2 * self.priorCenter[0]) // 3
                    currentCenter[1] = (currentCenter[1] + 2 * self.priorCenter[1]) // 3
                    # Hopefully the index is 0 since the primary user is user with the biggest face;
                    print('User tracking thread with Face Detection (end): the primary user with index %s is detected successfully.' % index)
                    self.priorCenter = currentCenter
                    self.faceNotFound = False
                    break
                if index == len(faces) - 1:
                    self.faceNotFound = True
                    print('User tracking thread with Face Detection (end): the primary user is gone.')
        else:
            # trying to find face from eye detection
            eyes = self.eye_cascade.detectMultiScale(gray_frame02, 1.1, 2, minSize=(30, 30))
            avg_x, avg_y = 0, 0
            if len(eyes) > 0:
                for (x, y, w, h) in eyes:
                    avg_x = avg_x + x + w // 2
                    avg_y = avg_y + y + h // 2
                center_face_possible = [avg_x // len(eyes), avg_y // len(eyes)]
                if self.faceNotFound:
                    self.priorCenter = center_face_possible
                    self.faceNotFound = False
                    print('User tracking thread with Eyes Detection (end): the first person detected by the algorithm becomes the primary user.')
                elif abs(center_face_possible[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                        center_face_possible[1] - self.priorCenter[1]) < self.frame_height // 6:
                    if abs(center_face_possible[0] - self.priorCenter[0]) < 7 and abs(
                            center_face_possible[1] - self.priorCenter[1]) < 7:
                        center_face_possible = self.priorCenter
                    center_face_possible[0] = (center_face_possible[0] + 2 * self.priorCenter[0]) // 3
                    center_face_possible[1] = (center_face_possible[1] + 2 * self.priorCenter[1]) // 3
                    self.priorCenter = center_face_possible
                    self.faceNotFound = False
                    print('User tracking thread with Eyes Detection (end): detecting the primary user successfully.')
                else:
                    self.faceNotFound = True
                    print('User tracking thread with Eyes Detection (end): the primary user is gone.')

            else:
                self.faceNotFound = True
                print('User tracking thread with Eyes & Face Detection (end): no user is detected.')

        if self.faceNotFound:
            self.tracking_failed.emit()
        else:
            time.sleep(2)


class MyThread6_1(QThread):
    """
    Compared with the MyThread6 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    """
    tracking_failed = pyqtSignal()

    def __init__(self, parent):
        super(MyThread6_1, self).__init__(parent)
        self.parent = parent
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_eye.xml')
        self.priorCenter = [0,0]  # the position of the center point of the user face which is given by account thread;
        self.faceNotFound = True  # This means that there is no user detected in the last frame or the first time;
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.frame_width = 600  # It is currently specified manually and is the corresponding width of the camera width;
        self.frame_height = 450
        self.status = True


    def run(self):
        try:
            self.faceNotFound = True
            self.status = True
            while self.status:
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)
                gray_frame01 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_frame02 = cv2.equalizeHist(gray_frame01)  # attention one
                faces = self.face_cascade.detectMultiScale(gray_frame02, 1.1, 3, minSize=(30, 30))
                print('User tracking thread begins')
                # the largest face will be the first face detected because classifiers will search something called an image pyramid
                if len(faces) > 0:
                    for index, (x, y, w, h) in enumerate(faces):
                        currentCenter = [x + w // 2, y + h // 2]
                        if self.faceNotFound:
                            self.priorCenter = currentCenter
                            self.faceNotFound = False  # This means that there is  user detected in the last frame;
                            print('User tracking thread with Face Detection (end): the first person detected by the algorithm becomes the primary user.')
                            break
                        elif abs(currentCenter[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                currentCenter[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(currentCenter[0] - self.priorCenter[0]) < 7 and abs(
                                    currentCenter[1] - self.priorCenter[1]) < 7:
                                currentCenter = self.priorCenter
                            currentCenter[0] = (currentCenter[0] + 2 * self.priorCenter[0]) // 3
                            currentCenter[1] = (currentCenter[1] + 2 * self.priorCenter[1]) // 3
                            # Hopefully the index is 0 since the primary user is user with the biggest face;
                            print(
                                'User tracking thread with Face Detection (end): the primary user with index %s is detected successfully.' % index)
                            self.priorCenter = currentCenter
                            self.faceNotFound = False
                            break
                        if index == len(faces) - 1:
                            self.faceNotFound = True
                            print('User tracking thread with Face Detection (end): the primary user is gone.')
                else:
                    # trying to find face from eye detection
                    eyes = self.eye_cascade.detectMultiScale(gray_frame02, 1.1, 2, minSize=(30, 30))
                    avg_x, avg_y = 0, 0
                    if len(eyes) > 0:
                        for (x, y, w, h) in eyes:
                            avg_x = avg_x + x + w // 2
                            avg_y = avg_y + y + h // 2
                        center_face_possible = [avg_x // len(eyes), avg_y // len(eyes)]
                        if self.faceNotFound:
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            print(
                                'User tracking thread with Eyes Detection (end): the first person detected by the algorithm becomes the primary user.')
                        elif abs(center_face_possible[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                center_face_possible[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(center_face_possible[0] - self.priorCenter[0]) < 7 and abs(
                                    center_face_possible[1] - self.priorCenter[1]) < 7:
                                center_face_possible = self.priorCenter
                            center_face_possible[0] = (center_face_possible[0] + 2 * self.priorCenter[0]) // 3
                            center_face_possible[1] = (center_face_possible[1] + 2 * self.priorCenter[1]) // 3
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            print(
                                'User tracking thread with Eyes Detection (end): detecting the primary user successfully.')
                        else:
                            self.faceNotFound = True
                            print('User tracking thread with Eyes Detection (end): the primary user is gone.')

                    else:
                        self.faceNotFound = True
                        print('User tracking thread with Eyes & Face Detection (end): no user is detected.')

                if self.faceNotFound:
                    self.status = False
                    self.tracking_failed.emit()
                else:
                    time.sleep(2)
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in user-tracking thread!------------------------***')


class MyThread6_2(QThread):
    """
    Compared with the MyThread6 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    """
    tracking_failed = pyqtSignal()

    def __init__(self, parent):
        super(MyThread6_2, self).__init__(parent)
        self.parent = parent
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_eye.xml')
        self.priorCenter = [0,0]  # the position of the center point of the user face which is given by account thread;
        self.faceNotFound = True  # This means that there is no user detected in the last frame or the first time;
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.frame_width = 600  # It is currently specified manually and is the corresponding width of the camera width;
        self.frame_height = 450
        self.status = True


    def run(self):
        try:
            self.faceNotFound = True
            self.status = True
            while self.status:
                _, self.frame = self.parent.user_interface.camera.read()
                img = cv2.cvtColor(self.frame, 0)
                gray_frame01 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_frame02 = cv2.equalizeHist(gray_frame01)  # attention one
                faces = self.face_cascade.detectMultiScale(gray_frame02, 1.1, 3, minSize=(30, 30))
                print('User tracking thread begins')
                # the largest face will be the first face detected because classifiers will search something called an image pyramid
                if len(faces) > 0:
                    for index, (x, y, w, h) in enumerate(faces):
                        currentCenter = [x + w // 2, y + h // 2]
                        if self.faceNotFound:
                            self.priorCenter = currentCenter
                            self.faceNotFound = False  # This means that there is  user detected in the last frame;
                            print('User tracking thread with Face Detection (end): the first person detected by the algorithm becomes the primary user.')
                            break
                        elif abs(currentCenter[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                currentCenter[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(currentCenter[0] - self.priorCenter[0]) < 7 and abs(
                                    currentCenter[1] - self.priorCenter[1]) < 7:
                                currentCenter = self.priorCenter
                            currentCenter[0] = (currentCenter[0] + 2 * self.priorCenter[0]) // 3
                            currentCenter[1] = (currentCenter[1] + 2 * self.priorCenter[1]) // 3
                            # Hopefully the index is 0 since the primary user is user with the biggest face;
                            print(
                                'User tracking thread with Face Detection (end): the primary user with index %s is detected successfully.' % index)
                            self.priorCenter = currentCenter
                            self.faceNotFound = False
                            break
                        if index == len(faces) - 1:
                            self.faceNotFound = True
                            print('User tracking thread with Face Detection (end): the primary user is gone.')
                else:
                    # trying to find face from eye detection
                    eyes = self.eye_cascade.detectMultiScale(gray_frame02, 1.1, 2, minSize=(30, 30))
                    avg_x, avg_y = 0, 0
                    if len(eyes) > 0:
                        for (x, y, w, h) in eyes:
                            avg_x = avg_x + x + w // 2
                            avg_y = avg_y + y + h // 2
                        center_face_possible = [avg_x // len(eyes), avg_y // len(eyes)]
                        if self.faceNotFound:
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            print(
                                'User tracking thread with Eyes Detection (end): the first person detected by the algorithm becomes the primary user.')
                        elif abs(center_face_possible[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                center_face_possible[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(center_face_possible[0] - self.priorCenter[0]) < 7 and abs(
                                    center_face_possible[1] - self.priorCenter[1]) < 7:
                                center_face_possible = self.priorCenter
                            center_face_possible[0] = (center_face_possible[0] + 2 * self.priorCenter[0]) // 3
                            center_face_possible[1] = (center_face_possible[1] + 2 * self.priorCenter[1]) // 3
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            print(
                                'User tracking thread with Eyes Detection (end): detecting the primary user successfully.')
                        else:
                            self.faceNotFound = True
                            print('User tracking thread with Eyes Detection (end): the primary user is gone.')

                    else:
                        self.faceNotFound = True
                        print('User tracking thread with Eyes & Face Detection (end): no user is detected.')

                if self.faceNotFound:
                    self.status = False
                    self.tracking_failed.emit()
                else:
                    time.sleep(3)
        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in user-tracking thread!------------------------***')


class MyThread6_3(QThread):
    """
    Compared with the MyThread6 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    The fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    """
    tracking_failed = pyqtSignal()

    def __init__(self, parent):
        super(MyThread6_3, self).__init__(parent)
        self.parent = parent
        self.face_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier('C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_eye.xml')
        self.priorCenter = [0,0]  # the position of the center point of the user face which is given by account thread;
        self.faceNotFound = True  # This means that there is no user detected in the last frame or the first time;
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.frame_width = 600  # It is currently specified manually and is the corresponding width of the camera width;
        self.frame_height = 450
        self.status = True


    def run(self):
        try:
            self.faceNotFound = True
            self.status = True
            while self.status:
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)
                gray_frame01 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_frame02 = cv2.equalizeHist(gray_frame01)  # attention one
                faces = self.face_cascade.detectMultiScale(gray_frame02, 1.1, 3, minSize=(30, 30))
                print('User tracking thread begins')
                # the largest face will be the first face detected because classifiers will search something called an image pyramid
                if len(faces) > 0:
                    for index, (x, y, w, h) in enumerate(faces):
                        currentCenter = [x + w // 2, y + h // 2]
                        if self.faceNotFound:
                            self.priorCenter = currentCenter
                            self.faceNotFound = False  # This means that there is  user detected in the last frame;
                            print('User tracking thread with Face Detection (end): the first person detected by the algorithm becomes the primary user.')
                            break
                        elif abs(currentCenter[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                currentCenter[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(currentCenter[0] - self.priorCenter[0]) < 7 and abs(
                                    currentCenter[1] - self.priorCenter[1]) < 7:
                                currentCenter = self.priorCenter
                            currentCenter[0] = (currentCenter[0] + 2 * self.priorCenter[0]) // 3
                            currentCenter[1] = (currentCenter[1] + 2 * self.priorCenter[1]) // 3
                            # Hopefully the index is 0 since the primary user is user with the biggest face;
                            print(
                                'User tracking thread with Face Detection (end): the primary user with index %s is detected successfully.' % index)
                            self.priorCenter = currentCenter
                            self.faceNotFound = False
                            break
                        if index == len(faces) - 1:
                            self.faceNotFound = True
                            print('User tracking thread with Face Detection (end): the primary user is gone.')
                else:
                    # trying to find face from eye detection
                    eyes = self.eye_cascade.detectMultiScale(gray_frame02, 1.1, 2, minSize=(30, 30))
                    avg_x, avg_y = 0, 0
                    if len(eyes) > 0:
                        for (x, y, w, h) in eyes:
                            avg_x = avg_x + x + w // 2
                            avg_y = avg_y + y + h // 2
                        center_face_possible = [avg_x // len(eyes), avg_y // len(eyes)]
                        if self.faceNotFound:
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            print(
                                'User tracking thread with Eyes Detection (end): the first person detected by the algorithm becomes the primary user.')
                        elif abs(center_face_possible[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                center_face_possible[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(center_face_possible[0] - self.priorCenter[0]) < 7 and abs(
                                    center_face_possible[1] - self.priorCenter[1]) < 7:
                                center_face_possible = self.priorCenter
                            center_face_possible[0] = (center_face_possible[0] + 2 * self.priorCenter[0]) // 3
                            center_face_possible[1] = (center_face_possible[1] + 2 * self.priorCenter[1]) // 3
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            print(
                                'User tracking thread with Eyes Detection (end): detecting the primary user successfully.')
                        else:
                            self.faceNotFound = True
                            print('User tracking thread with Eyes Detection (end): the primary user is gone.')
                    else:
                        self.faceNotFound = True
                        print('User tracking thread with Eyes & Face Detection (end): no user is detected.')

                if self.faceNotFound:
                    self.status = False
                    self.tracking_failed.emit()
                else:
                    time.sleep(2)
                if  not self.parent.timer1.isActive():
                    self.status = False  # close itself since the payment system is in stand-by status;


        except BaseException:
            print(''.join(traceback.format_exception(*sys.exc_info())))
            print('***------------------------Be careful! Error occurs in user-tracking thread!------------------------***')


class MyThread6_3_1(QThread):
    """
    Compared with the MyThread6 class, one main difference is the while loop in its run();
    Another difference is that the refresh of the image should be inside the while loop;
    The third difference is that the thread stops itself since the while loop;
    The fourth difference is it checks the status of the QTimer to close itself since it is not closed after one purchase logically;
    Compared with the MyThread6_3 class, the logging module is introduced to this module at first time.
    """
    tracking_failed = pyqtSignal()

    def __init__(self, parent, logger_name='hobin', *,
                 face_classifer_path='C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml',
                 eyes_classifer_path='C:\\Users\\hobin\\AppData\Local\\Continuum\\anaconda3\\envs\\Python36_Qt5\\Library\\etc\\haarcascades\\haarcascade_eye.xml',
                  **kwargs):
        super(MyThread6_3_1, self).__init__(parent)
        # the first way to configuring the parameters, almost all parameters get their value from those named keyword arguments.
        self.face_cascade = cv2.CascadeClassifier(face_classifer_path)
        self.eye_cascade = cv2.CascadeClassifier(eyes_classifer_path)

        # the second way to configure the parameters, almost all parameters get their value from the keyword argument 'kwargs'.
        # self.face_cascade = cv2.CascadeClassifier(kwargs['face_classifer_path'])
        # self.eye_cascade = cv2.CascadeClassifier(kwargs['eyes_classifer_path'])

        # some variables
        self.parent = parent
        self.mylogger6_3_1 = logging.getLogger(logger_name)
        self.priorCenter = [0,0]  # the position of the center point of the user face which is given by account thread;
        self.faceNotFound = True  # This means that there is no user detected in the last frame or the first time;
        self.frame = None  # This variable is assigned by its family-like object and it requires a ndarray type;
        self.frame_width = 600  # It is currently specified manually and is the corresponding width of the camera width;
        self.frame_height = 450
        self.status = True
        self.mylogger6_3_1.info('The initialization of the user-tracking thread is successful.')


    def run(self):
        try:
            self.faceNotFound = True
            self.status = True
            while self.status:
                self.frame = self.parent.main_widget.mainlayout.rightlayout.secondlayout.thread1.frame
                img = cv2.cvtColor(self.frame, 0)
                gray_frame01 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_frame02 = cv2.equalizeHist(gray_frame01)  # attention one
                faces = self.face_cascade.detectMultiScale(gray_frame02, 1.1, 3, minSize=(30, 30))
                # print('User tracking thread begins')
                self.mylogger6_3_1.info('User tracking thread begins')
                # the largest face will be the first face detected because classifiers will search something called an image pyramid
                if len(faces) > 0:
                    for index, (x, y, w, h) in enumerate(faces):
                        currentCenter = [x + w // 2, y + h // 2]
                        if self.faceNotFound:
                            self.priorCenter = currentCenter
                            self.faceNotFound = False  # This means that there is  user detected in the last frame;
                            # print('User tracking thread with Face Detection (end): the first person detected by the algorithm becomes the primary user.')
                            self.mylogger6_3_1.info('User tracking thread with Face Detection (end): the first person detected by the algorithm becomes the primary user.')
                            break
                        elif abs(currentCenter[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                currentCenter[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(currentCenter[0] - self.priorCenter[0]) < 7 and abs(
                                    currentCenter[1] - self.priorCenter[1]) < 7:
                                currentCenter = self.priorCenter
                            currentCenter[0] = (currentCenter[0] + 2 * self.priorCenter[0]) // 3
                            currentCenter[1] = (currentCenter[1] + 2 * self.priorCenter[1]) // 3
                            # Hopefully the index is 0 since the primary user is user with the biggest face;
                            # print('User tracking thread with Face Detection (end): the primary user with index %s is detected successfully.' % index)
                            self.mylogger6_3_1.info('User tracking thread with Face Detection (end): the primary user with index %s is detected successfully.' % index)
                            self.priorCenter = currentCenter
                            self.faceNotFound = False
                            break
                        if index == len(faces) - 1:
                            self.faceNotFound = True
                            # print('User tracking thread with Face Detection (end): the primary user is gone.')
                            self.mylogger6_3_1.info('User tracking thread with Face Detection (end): the primary user is gone.')
                else:
                    # trying to find face from eye detection
                    eyes = self.eye_cascade.detectMultiScale(gray_frame02, 1.1, 2, minSize=(30, 30))
                    avg_x, avg_y = 0, 0
                    if len(eyes) > 0:
                        for (x, y, w, h) in eyes:
                            avg_x = avg_x + x + w // 2
                            avg_y = avg_y + y + h // 2
                        center_face_possible = [avg_x // len(eyes), avg_y // len(eyes)]
                        if self.faceNotFound:
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            # print('User tracking thread with Eyes Detection (end): the first person detected by the algorithm becomes the primary user.')
                            self.mylogger6_3_1.info('User tracking thread with Eyes Detection (end): the first person detected by the algorithm becomes the primary user.')
                        elif abs(center_face_possible[0] - self.priorCenter[0]) < self.frame_width // 6 and abs(
                                center_face_possible[1] - self.priorCenter[1]) < self.frame_height // 6:
                            if abs(center_face_possible[0] - self.priorCenter[0]) < 7 and abs(
                                    center_face_possible[1] - self.priorCenter[1]) < 7:
                                center_face_possible = self.priorCenter
                            center_face_possible[0] = (center_face_possible[0] + 2 * self.priorCenter[0]) // 3
                            center_face_possible[1] = (center_face_possible[1] + 2 * self.priorCenter[1]) // 3
                            self.priorCenter = center_face_possible
                            self.faceNotFound = False
                            # print('User tracking thread with Eyes Detection (end): detecting the primary user successfully.')
                            self.mylogger6_3_1.info('User tracking thread with Eyes Detection (end): detecting the primary user successfully.')
                        else:
                            self.faceNotFound = True
                            # print('User tracking thread with Eyes Detection (end): the primary user is gone.')
                            self.mylogger6_3_1.info('User tracking thread with Eyes Detection (end): the primary user is gone.')
                    else:
                        self.faceNotFound = True
                        # print('User tracking thread with Eyes & Face Detection (end): no user is detected.')
                        self.mylogger6_3_1.info('User tracking thread with Eyes & Face Detection (end): no user is detected.')

                if self.faceNotFound:
                    self.status = False
                    self.tracking_failed.emit()
                else:
                    time.sleep(2)
                if  not self.parent.timer1.isActive():
                    self.status = False  # close itself since the payment system is in stand-by status;

        except BaseException:
            # print(''.join(traceback.format_exception(*sys.exc_info())))
            self.mylogger6_3_1.error(''.join(traceback.format_exception(*sys.exc_info())))
            # print('***------------------------Be careful! Error occurs in user-tracking thread!------------------------***')
            self.mylogger6_3_1.error('***------------------------Be careful! Error occurs in user-tracking thread!------------------------***')


if __name__ == '__main__':
    pass

