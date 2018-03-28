#-*- coding=utf-8 -*-
from PyQt5.QtCore import QObject
from PyQt5.QtQuick import QQuickImageProvider,QQuickView,QQuickPaintedItem,QQuickWindow
from PyQt5.QtGui import QGuiApplication,QImage,QPainter,QPixmap
from PyQt5.QtCore import QUrl,QPoint,QAbstractListModel,QObject,Qt,pyqtSlot,QTextCodec
from PyQt5.QtQml import QQmlImageProviderBase,qmlRegisterType,QQmlApplicationEngine,QQmlComponent
from PyQt5.QtWidgets import QApplication 
from customOpenCV import CustomOpenCVItem
import os,sys


QTextCodec.setCodecForLocale(QTextCodec.codecForName("utf-8"));

deafaultUserPic = "./Images/DeafaultPortrait.jpg"

class PicItem(QQuickPaintedItem):
    """docstring for PicItem"""
    def __init__(self, parent = None):
        super(PicItem, self).__init__(parent)
        self._image = QImage(deafaultUserPic)
        if self._image.isNull():
            print("image open fail")

    def paint(self, painter):

    #        print('contentsSize ',self.contentsSize())
    #        print('contentsBoundingRect ',self.contentsBoundingRect())
        contentSize = self.contentsBoundingRect()
        x1,y1,x2,y2 = contentSize.getRect()
        if self._image.isNull():
            print("None Image!!")
            return False
        painter.drawImage(QPoint(0, 0), self._image.scaled(x2,y2, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    #        painter.drawImage(QPoint(self.mPosX, self.mPosY), self._image)#.scaled(self.contentsBoundingRect(),Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    #        painter.fillRect(self.contentsBoundingRect(), self._image); this doesn't work
            #print("damn")
    def updateImage(self,image):
        self._image = image
        self.update()



class CommodityPicItem(PicItem):
    """docstring for CommodityPicItem"""

    picList = {}
    def __init__(self,  parent = None):
        super(CommodityPicItem, self).__init__(parent)
        if len(self.picList)==0:
            self.initPic()
        self.updateImage("define")

    def initPic(self):
        path = ".\\Images\\"
        for r, ds, fs in os.walk(path):
            for fn in fs:
                if not (os.path.splitext(fn)[-1] in ('.jpg', '.JPG', '.png', '.PNG')):
                    continue
                fname = os.path.join(r, fn)
                #print(fn)
                self.picList[fn.split(".",1)[0]]=fname

    @pyqtSlot(str)
    def setCommodImage(self,name):
        if name in self.picList:
            self.updateImage(QImage(self.picList[name]))
        else:
            self.updateImage(QImage(self.picList["define"]))





class PaymentInterface(QQmlApplicationEngine):
    """docstring for PaymentInterface"""
    def __init__(self,faceCameraId=0):
        super(PaymentInterface, self).__init__()
        qmlRegisterType(CustomOpenCVItem,'MyModel',1,0,'CustomOpenCVItem')
        qmlRegisterType(PicItem,'MyModel',1,0,'PicItem')
        qmlRegisterType(CommodityPicItem,'MyModel',1,0,'CommodityPicItem')

        self.load(QUrl(".\\QML\\main.qml"))
        self.quit.connect(self.onclose)
        if len(self.rootObjects())==0:
            print("load qml fail!!!")
            sys.exit()
        self.__rootobject = self.rootObjects()[0]
        self.__faceCameraId = faceCameraId


    #return class CustomOpenCVItem or False
    def getCameraPersionItem(self):
        return self.__rootobject.getCameraPersionItem()


    #cant use
    def getCameraCommodityItem(self):
        return self.__rootobject.getCameraCommodityItem()

    #type(image) = QImage, type(name) = str
    def setUserInfo(self,image,name):
        if self.__rootobject.getUserItem() == False:
            return False
        self.__rootobject.getUserItem().updateImage(image)
        self.__rootobject.setUserName(name)


    #show Settlement view
    def toSettlement(self):
        self.__rootobject.toSettlement()
        self.getCameraPersionItem().setCameraID(self.__faceCameraId)
        self.camera = self.getCameraPersionItem()._capture


    #show WellCome view
    def toWelcome(self):
        self.__rootobject.outSettlement()

    def setfaceCameraID(self,faceCameraId):
        if not self.getCameraPersionItem() :
            self.getCameraPersionItem().setCameraID(faceCameraId)

    def showTooMuchCommodity(self):
        self.__rootobject.showTooMuchCommodity()

    def addCommodity(self,picid='define', name='default',info="  ",weight='0',price='0'):
        self.__rootobject.addCommodity(picid,name,info,weight,price)

    def clearCommoditylist(self):
        self.__rootobject.cleanCommodityList()

    #set the sum price
    def setSumPrice(self,price):
        self.__rootobject.setSumPrice(price)

    def showHandpay(self):
        self.__rootobject.showHandpay()

    def hideHandpay(self):
        self.__rootobject.hideHandpay()

    def startHandpay(self):
        self.__rootobject.startHandpay()

    def stopHandpay(self):
        self.__rootobject.stopHandpay()

    def setNoneUser(self):
        self.setUserInfo(QImage(deafaultUserPic),"Name")

    def getQRCodeItem(self):
        return self.__rootobject.getQRCode()

    def setQRCode(self,image):
        if not self.getQRCodeItem():
            return False
        self.getQRCodeItem().updateImage(image)
        self.getQRCodeItem().setVisible(True)

    def hideQRCode(self):
        if not self.getQRCodeItem():
            return False
        self.getQRCodeItem().setVisible(False)

    #type = 1:success 2:fail  0:hideAll
    def showpayReslt(self,type):
        self.__rootobject.showpayReslt(type)

    #isHandpay  True:hide NohandPayImage False:show NohandPayImage
    def setHandpayable(self,isHandpay):
        self.__rootobject.setHandpayable(isHandpay)

    def onclose(self):
        self.camera.release()


if __name__ == '__main__':

    app = QGuiApplication([])
    view = PaymentInterface()
    #context.updataImage()
    app.exec_()


