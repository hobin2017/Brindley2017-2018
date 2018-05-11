#-*- coding=utf-8 -*-
from PyQt5.QtCore import QObject
from PyQt5.QtQuick import QQuickImageProvider,QQuickView,QQuickPaintedItem,QQuickWindow
from PyQt5.QtGui import QGuiApplication,QImage,QPainter,QPixmap
from PyQt5.QtCore import QUrl,QPoint,QAbstractListModel,QObject,Qt,pyqtSlot,QTextCodec,pyqtSignal,QThread,QRect
from PyQt5.QtQml import QQmlImageProviderBase,qmlRegisterType,QQmlApplicationEngine,QQmlComponent
from PyQt5.QtWidgets import QApplication 
from customOpenCV import CustomOpenCVItem
import os
import sys,cv2
from SkuSysn import SkuSysnServer
import numpy as np
import requests
from SkuSysn import * 

QTextCodec.setCodecForLocale(QTextCodec.codecForName("utf-8"));



class PicItem(QQuickPaintedItem):
	"""docstring for PicItem"""
	setImageSignal = pyqtSignal()
	roundmask = QImage("./Images/mask.png")
	def __init__(self, parent = None):
		super(PicItem, self).__init__(parent)
		self._image = QImage("./Images/define.png")
		self.htw = None
		self.update()
		if self._image.isNull():
			print("image open fail =./Images/define.png ")
		
	def paint(self, painter):
	#		print('contentsSize ',self.contentsSize())
	#		print('contentsBoundingRect ',self.contentsBoundingRect())
		
		contentSize = self.contentsBoundingRect()
		x1,y1,x2,y2 = contentSize.getRect()
		
		if self._image.isNull():
			print("None Image!!")
			return False
		if self.htw == None:
			painter.setCompositionMode(QPainter.CompositionMode_Source)
			painter.fillRect(contentSize, Qt.transparent) 
			painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
			painter.drawImage(0,0, self.roundmask.scaled(x2,y2, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
			painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
			painter.drawImage(QPoint(0, 0), self._image.scaled(x2,y2, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
			painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
		else:
			tx = (x2 - y2*self.htw)/2
			painter.drawImage(QPoint(tx, 0), self._image.scaled(x2,y2, Qt.KeepAspectRatio, Qt.SmoothTransformation))
#		painter.drawImage(QPoint(self.mPosX, self.mPosY), self._image)#.scaled(self.contentsBoundingRect(),Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
#		painter.fillRect(self.contentsBoundingRect(), self._image); this doesn't work
		#print("damn")
	def updateImage(self,image):
		self._image = image
		#self.htw = self._image.size().height() / self._image.size().width()
		#print(self.htw)
		self.update()



class CommodityPicItem(PicItem):
	"""docstring for CommodityPicItem"""

	picList = {}
	def __init__(self,  parent = None):
		super(CommodityPicItem, self).__init__(parent)
		if len(self.picList)==0:
			self.initPic()
		#self.setCommodImage("define")
		
	#@pyqtSlot()
	@classmethod
	def initPic(self):
		print("init Pic")
		path = "./Images/"
		for r, ds, fs in os.walk(path):
			for fn in fs:
				if not (os.path.splitext(fn)[-1] in ('.jpg', '.JPG', '.png', '.PNG')):
					continue
				fname = os.path.join(r, fn)
				self.picList[fn.split(".",1)[0]]=QImage(fname)
		path = "./skuPic/"
		for r, ds, fs in os.walk(path):
			for fn in fs:
				if not (os.path.splitext(fn)[-1] in ('.jpg', '.JPG', '.png', '.PNG')):
					continue
				fname = os.path.join(r, fn)
				self.picList[fn.split(".",1)[0]]=QImage(fname)
				



	@pyqtSlot(str)
	def setCommodImage(self,name):
		print("setCommodImage : ",name)
		if name in self.picList:
			self.updateImage(self.picList[name])
		else:
			self.updateImage(self.picList["define"])

	def updateImage(self,image):
		self.setWidth(1)
		self.setHeight(1)
		self._image = image
		self.htw = self._image.size().height() / self._image.size().width()
		self.update()
		self.setImageSignal.emit()

		
		
def handAppQRcode(path):
	if os.path.exists(path):
		pig = cv2.imread(path)
		
		backimg = np.ones((300,300,3),dtype=np.uint8)
		backimg*=255
		#backimg[:] = [255,255,255]
		haf = int(pig.shape[0]/2)
		#pig = cv2.addWeighted(tmp,0,pig,1,0)
		backimg[150-haf:150+haf,150-haf:150+haf] = pig
		cv2.imwrite(path,backimg)



class MainWindow(QQmlApplicationEngine):
	"""docstring for MainWindow"""
	def __init__(self,cameraId=0,cameraW=640,cameraH=480,sysService=None):
		super(MainWindow, self).__init__()
		qmlRegisterType(CustomOpenCVItem,'MyModel',1,0,'CustomOpenCVItem')
		qmlRegisterType(PicItem,'MyModel',1,0,'PicItem')
		qmlRegisterType(CommodityPicItem,'MyModel',1,0,'CommodityPicItem')

	#	self.sysService = SkuSysnServer(dbHost=dbHost,user=user,password=password,dbname=dbname,store_id=str(storeid),apiUrl=apiUrl)#加载同步服务
		if sysService!=None:
			self.sysService = sysService
			self.sysService.sysFinshSignal.connect(CommodityPicItem.initPic)
			self.sysService.timoutEvent()

		self.load(QUrl("QML/main.qml"))

		if len(self.rootObjects())==0:
			print("load qml fail!!!")
			sys.exit()
		self.rootobject = self.rootObjects()[0]

		self.storeid = 17
		#self.initLittleAppQRcode()
		
		self.cameraItem = self.rootobject.getCameraPersionItem()
		self.cameraItem.setWidthAndHeight(cameraW,cameraH)
		self.cameraItem.setCameraID(cameraId)
		self._capture = self.rootobject.getCameraPersionItem()._capture

		self.qrItem = self.rootobject.getLittleApp()
		self.qrItem.htw = 1
		


	#return class CustomOpenCVItem or False
	def getCamera(self):
		return self.cameraItem._capture


	def getFaceImage(self):
		return self.rootobject.getHeadImage()

	#show Settlement view
	def toSettlement(self):
		self.rootobject.setScanGif(True)
		self.rootobject.toSettlementView()

	#show WellCome view
	def toWelcome(self):
		self.rootobject.toWelComeView()

	#正在支付界面 image 摄像头截图
	def toPayingView(self,image=None):
		if image!=None and (not image.isNull()):
			self.getFaceImage().updateImage(image)
		else:
			s = QImage("./Images/timg.jpg")
			print(type(s))
			self.getFaceImage().updateImage(s)
		self.stopHandGif()
		self.rootobject.toPaying()
		

	#未注册界面 image 头像图片 ，qrimage二维码图片
	def toRegisterView(self,image=None,qrimage=None):
		#self.initLittleAppQRcode()
		i = 1
		if image!=None and (not image.isNull()):
			self.getFaceImage().updateImage(image)
		else:
			i=0
		if qrimage!=None:
			self.qrItem.setVisible(True)
			self.qrItem.updateImage(qrimage)
		else:
			self.qrItem.setVisible(False)
		self.rootobject.toRegisterView(i)

	#支付成功界面
	def toPaySuccessView(self,image=None,name = None):
		if image!=None and (not image.isNull()):
			self.getFaceImage().updateImage(image)
	#	else:
	#		self.getFaceImage().updateImage(QImage("./Images/timg.jpg"))
		if name!=None:
			self.rootobject.setUserName(name)
		else:
			self.rootobject.setUserName("")
		self.rootobject.toPaySuccess()
	
	#支付失败界面
	def toPayFailView(self,image=None,name = None):
		if image!=None and (not image.isNull()):
			self.getFaceImage().updateImage(image)
	#	else:
	#		self.getFaceImage().updateImage(QImage("./Images/timg.jpg"))
		if name!=None:
			self.rootobject.setUserName(name)
		self.rootobject.toPayFail()

	#离店界面
	def toleaveStore(self):
		self.rootobject.toLeaveStore()

	#弹出错误提示
	#id=0 未识别 ，id=1 设备不可用, di=2 商品过多
	def showErrorInfo(self,id):
		self.rootobject.showError(id)

	#隐藏错误提示
	def hideErrorInfo(self):
		self.rootobject.hideError()

	#检测到商品，正在识别界面
	def toIdentifingView(self):
		self.rootobject.toIdentifing()

	#添加商品
	#picid = enum[1,2,3,4] ,name = str,image=sku_id,price=str
	def addCommodity(self,picid,name,image,price):
		self.rootobject.getPicObject(picid).setCommodImage(image)
		if len(name)>13:
			name = name[:12]+"..."
		self.rootobject.setCommodity(picid,name,price)
	
	#清空商品
	def cleanCommodity(self):
		self.rootobject.cleanCommodity()


	#sum price
	def setSumPrice(self,price):
		self.rootobject.setSumPrice(price)

	#显示圈手Gif , x,y手势中心点,frame 帧 Numpy.array
	def showHandGif(self,x,y,frame,width=200):
		self.cameraItem.ispaint = False
		self.cameraItem._frame = frame
		self.cameraItem.setHandPos(x,y)
		if width % 2!=0:
			width+=1
		self.cameraItem.handWidth=width
		self.rootobject.setScanGif(False)
	
	def stopHandGif(self):
		self.cameraItem.ispaint = True
		self.rootobject.setScanGif(True)
		self.cameraItem.stopHandGif()

	#提示移动位置 以 识别人脸 ， 自动隐藏
	def showFaceCantIdentify(self):
		self.rootobject.showFaceCantIdentify()







if __name__ == '__main__':

	app = QGuiApplication([])  
	#handAppQRcode("Images/app.jpg")


	sysSevice = SkuSysnServer()
	view = MainWindow(sysService=sysSevice)
	

	#ret, frame = view._capture.read()
	#view.addCommodity(1,"豆腐","logo","15.5")
	#view.toSettlement()
	#view.toPayingView(QImage("./Images/appbak.jpg"))
	#view.showHandGif(300,300,frame)
	#view.getFaceImage().updateImage(QImage("./Images/app.jpg"))
	#context.updataImage()
	app.exec_()  


