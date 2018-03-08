#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-


from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5 import QtCore
from PyQt5 import QtWidgets

try:
    import cv2
    import sys
    import numpy


    from PyQt5.QtQuick import QQuickPaintedItem
    from PyQt5.QtCore import (pyqtProperty, pyqtSignal, Q_CLASSINFO, QCoreApplication, QDate, QObject, QTime, QUrl)
    from PyQt5.QtCore import QTimerEvent
    from PyQt5.QtCore import QTimer

    from PyQt5.QtCore import qDebug
    from PyQt5.QtGui import QPainter
    from PyQt5.QtWidgets import QStyleOptionGraphicsItem
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtWidgets import QGraphicsItem

    from PyQt5.QtQuick import QQuickItem
    from PyQt5.QtCore import pyqtProperty

    from PyQt5.QtCore import Qt
    from PyQt5.QtCore import QSize
    from PyQt5.QtCore import QPoint
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QColor
    from PyQt5.QtGui import QImage
except Exception as e:
    print("Error in importing modules ",e)



def gray2qimage(gray):
        """Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
        colormap.  The first dimension represents the vertical image axis.

        ATTENTION: This QImage carries an attribute `ndimage` with a
        reference to the underlying numpy array that holds the data. On
        Windows, the conversion into a QPixmap does not copy the data, so
        that you have to take care that the QImage does not get garbage
        collected (otherwise PyQt will throw away the wrapper, effectively
        freeing the underlying memory - boom!)."""
        if len(gray.shape) != 2:
                raise ValueError("gray2QImage can only convert 2D arrays")

        gray = numpy.require(gray, numpy.uint8, 'C')

        h, w = gray.shape

        result = QImage(gray.data, w, h, QImage.Format_Indexed8)
        result.ndarray = gray
        for i in range(256):
                result.setColor(i, QColor(i, i, i).rgb())
        return result

def rgb2qimage(rgb):
        """Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
        have three dimensions with the vertical, horizontal and RGB image axes.

        ATTENTION: This QImage carries an attribute `ndimage` with a
        reference to the underlying numpy array that holds the data. On
        Windows, the conversion into a QPixmap does not copy the data, so
        that you have to take care that the QImage does not get garbage
        collected (otherwise PyQt will throw away the wrapper, effectively
        freeing the underlying memory - boom!)."""
        if len(rgb.shape) != 3:
                raise ValueError("rgb2QImage can only convert 3D arrays")
        if rgb.shape[2] not in (3, 4):
                raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

        #h, w, channels = rgb.shape



        ## Qt expects 32bit BGRA data for color images:
        #bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
        #bgra[...,0] = rgb[...,2]
        #bgra[...,1] = rgb[...,1]
        #bgra[...,2] = rgb[...,0]
        #if rgb.shape[2] == 3:
                #bgra[...,3].fill(255)
                #fmt = QImage.Format_RGB32
        #else:
                #bgra[...,3] = rgb[...,3]
                #fmt = QImage.Format_ARGB32

        #result = QImage(bgra.data, w, h, fmt)
        #result.ndarray = bgra
        #return result
        height, width, bytesPerComponent = rgb.shape
        bytesPerLine = bytesPerComponent * width
        result  = QImage(rgb, width, height, bytesPerLine, QImage.Format_RGB888)
        return result.rgbSwapped()






class CustomOpenCVItem(QQuickPaintedItem):

    cameraIdChanged = pyqtSignal()
    activateVideoChanged = pyqtSignal()
    activateFaceRecognitionChanged = pyqtSignal()


    def __init__(self, parent = None):
        super(CustomOpenCVItem, self).__init__(parent)
#        self.setFlag(QQuickItem.ItemHasContents, False)
        print("init CustomOpenCVItem")
        self.activateVideoStream = True

        self.facialRecognition = False

        self.customCameraID = -1

        self.mOutH = 0 #image real rendering sizes
        self.mOutW = 0 #image real rendering sizes
        self.mImgratio = 16.0/9.0 # Default image ratio

        self.mPosX = 0 # top/left image coordinates, allow to render image in the center of the widget
        self.mPosY = 0 # top/left image coordinates, allow to render image in the center of the widget
        self._timer = QTimer(self) #This is for video capture
        self._capture = None
        self._frame = None
        self._image = None



    def getCameraID(self):
        return self.customCameraID

    def setCameraID(self, value):
        print('setCameraIDis ',value)
        if self.customCameraID != value or True:
            self.customCameraID = value

            try:
                if self._capture!=None:
                    self._capture.release()
                self._capture = cv2.VideoCapture(self.customCameraID)
                # size = (640,480)
#                self._capture.set(CV_CAP_PROP_FPS,30)
#                self._capture.set(4, size[0])
#                self._capture.set(5,size[1])
#                self._capture.set(6,30)
                ret, frame = self._capture.read()
                self._frame=frame
                height, width, depth = frame.shape

                self.cascPath = 'face_cascade.xml'
                self.faceCascade = cv2.CascadeClassifier(self.cascPath)
#                self.faceCascade.load(cascPath)

                self._image = self._build_image(frame)
                # Paint every 16 ms
                self._timer.timeout.connect(self.queryFrame)
                self._timer.start(16)
            except Exception as e:
                print("Error in openCV camera ID  ",e)
                sys.exit(0)



    def getFaceRecognitionState(self):
        return self.facialRecognition

    def setFaceRecognitionState(self,state):
        if self.facialRecognition != state:

            self.facialRecognition  = state

    def getVideoState(self):
        return self.activateVideoStream

    def setVideoState(self, state):
        if self._capture==None:
            return False
        if self.activateVideoStream != state:
            if state == False:
                self._capture.release()
                self._timer.stop()
            else:
                self.setCameraID(self.customCameraID)
            self.activateVideoStream  = state



    def paint(self, painter):

        contentSize = self.contentsBoundingRect()
        x1,y1,x2,y2 = contentSize.getRect()
        if self._image==None:
            return
        try:
            painter.drawImage(QPoint(self.mPosX, self.mPosY), self._image.scaled(x2,y2, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print("print fail !!",e)
     
    def create_blank(self,width, height, rgb_color=(0, 0, 0)):
       """Create new image(numpy array) filled with certain color in RGB"""
       # Create black blank image
       image = numpy.zeros((height, width, 3), numpy.uint8)

       # Since OpenCV uses BGR, convert the color first
       color = tuple(reversed(rgb_color))
       # Fill image with color
       image[:] = color

       return image

    def _build_image(self, array):
       if numpy.ndim(array) == 2:
           return gray2qimage(array)
       elif numpy.ndim(array) == 3:
           return rgb2qimage(array)
       raise ValueError("can only convert 2D or 3D arrays")


    def queryFrame(self):
        #frame = cv.QueryFrame(self._capture)
        if self._capture == None:
            return False
        ret, frame = self._capture.read()
        self._frame = frame
        self._image = self._build_image(frame).mirrored(True, False)
        self.update()


    cameraID = pyqtProperty(int, fget=getCameraID, fset= setCameraID, notify=cameraIdChanged)
    activateVideo = pyqtProperty(bool, fget=getVideoState, fset= setVideoState, notify=activateVideoChanged)
    activateFaceRecognition = pyqtProperty(bool, fget=getFaceRecognitionState, fset= setFaceRecognitionState, notify=activateFaceRecognitionChanged)



