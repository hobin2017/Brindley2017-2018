# -*- coding:UTF-8 -*-

import hashlib
from PyQt5.QtNetwork import QNetworkInterface
from PyQt5.QtWidgets import QDialog, QApplication,QProgressDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot,pyqtSignal
import platform,json,pickle
import sys,time,collections,requests
from datetime import datetime




def getDevMd5(deviceID,diskID, MAC,dtime, cipher='w2wJCnctEG09danPPI7SxQ=='):
	
	st = deviceID+diskID+MAC
	print(st)
	st1 = hashlib.md5(st.encode("utf-8")).hexdigest()+cipher
	st2 = hashlib.md5(st1.encode("utf-8")).hexdigest()+dtime
	st3 = hashlib.sha256(st2.encode("utf-8")).hexdigest()
	return st3


def getMac():
	NetWoerkList = QNetworkInterface.allInterfaces()
	targetNet = None
	for net in NetWoerkList:
		if net.flags() != QNetworkInterface.IsLoopBack and net.hardwareAddress() != "00:00:00:00:00:00":
			targetNet = net
			break
	if targetNet != None:
		return targetNet.hardwareAddress()
	else:
		return "00:00:00:00:00:00"


# 硬盘序列号
def win_getHardDiskId():
	import wmi
	c = wmi.WMI()
	encrypt_str = ""
	tmplist = []
	for physical_disk in c.Win32_DiskDrive():
		#print('disk id:', physical_disk.SerialNumber.strip())
		return physical_disk.SerialNumber.strip()


"""
	for physical_disk in c.Win32_DiskDrive():
		#encrypt_str = encrypt_str+physical_disk.SerialNumber.strip()
		print('disk id:', physical_disk.SerialNumber.strip())
		return physical_disk.SerialNumber.strip()
		#tmpdict = {}
		#tmpdict["Caption"] = physical_disk.Caption
		#tmpdict["Size"] = int(physical_disk.Size)/1000/1000/1000
		#tmplist.append(tmpdict)
	for cpu in c.Win32_Processor():#cpu 序列号
		encrypt_str = encrypt_str+cpu.ProcessorId.strip()
		print( "cpu id:", cpu.ProcessorId.strip())

	for board_id in c.Win32_BaseBoard():#主板序列号
		encrypt_str = encrypt_str+board_id.SerialNumber.strip()
		print( "main board id:",board_id.SerialNumber.strip())
	for mac in c.Win32_NetworkAdapter():#mac 地址（包括虚拟机的）

		print("mac addr:", mac.MACAddress)

	for bios_id in c.Win32_BIOS():#bios 序列号
		encrypt_str = encrypt_str+bios_id.SerialNumber.strip()
		print( "bios number:", bios_id.SerialNumber.strip())
		print( "encrypt_str:", encrypt_str)
"""


def linux_getHardDiskId():
	import fcntl
	import struct
	with open('/dev/sda', 'rb') as fd:
		# tediously derived from the monster struct defined in <hdreg.h>
		# see comment at end of file to verify
		hd_driveid_format_str = "@ 10H 20s 3H 8s 40s 2B H 2B H 4B 6H 2B I 36H I Q 152H"
		# Also from <hdreg.h>
		HDIO_GET_IDENTITY = 0x030d
		# How big a buffer do we need?
		sizeof_hd_driveid = struct.calcsize(hd_driveid_format_str)

		# ensure our format string is the correct size
		# 512 is extracted using sizeof(struct hd_id) in the c code
		assert sizeof_hd_driveid == 512

		# Call native function
		buf = fcntl.ioctl(fd, HDIO_GET_IDENTITY, " "*sizeof_hd_driveid)
		fields = struct.unpack(hd_driveid_format_str, buf)
		serial_no = fields[10].strip()
		#model = fields[15].strip()
		#print("Hard Disk Model: %s" % model)

		return serial_no.decode('ascii')


def getHardDiskId():
	try:
		sysstr = platform.system()
		if(sysstr == "Windows"):
			return win_getHardDiskId()
		elif(sysstr == "Linux"):
			return linux_getHardDiskId()
	except Exception as e:
		print("error:", e)
		return "SL3232414232"


class Ui_Dialog(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(557, 235)
		self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
		self.verticalLayout.setObjectName("verticalLayout")
		self.formLayout = QtWidgets.QFormLayout()
		self.formLayout.setObjectName("formLayout")
		self.label = QtWidgets.QLabel(Dialog)
		font = QtGui.QFont()
		font.setFamily("黑体")
		font.setPointSize(15)
		self.label.setFont(font)
		self.label.setObjectName("label")
		self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
		self.lineEdit_mac = QtWidgets.QLineEdit(Dialog)
		font = QtGui.QFont()
		font.setPointSize(20)
		self.lineEdit_mac.setFont(font)
		self.lineEdit_mac.setReadOnly(True)
		self.lineEdit_mac.setObjectName("lineEdit_mac")
		self.formLayout.setWidget(
			0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_mac)
		self.label_2 = QtWidgets.QLabel(Dialog)
		font = QtGui.QFont()
		font.setFamily("黑体")
		font.setPointSize(15)
		self.label_2.setFont(font)
		self.label_2.setObjectName("label_2")
		self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
		self.lineEdit_disk = QtWidgets.QLineEdit(Dialog)
		font = QtGui.QFont()
		font.setPointSize(20)
		self.lineEdit_disk.setFont(font)
		self.lineEdit_disk.setReadOnly(True)
		self.lineEdit_disk.setObjectName("lineEdit_disk")
		self.formLayout.setWidget(
			1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_disk)
		self.label_3 = QtWidgets.QLabel(Dialog)
		font = QtGui.QFont()
		font.setFamily("黑体")
		font.setPointSize(15)
		self.label_3.setFont(font)
		self.label_3.setObjectName("label_3")
		self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
		self.lineEdit_id = QtWidgets.QLineEdit(Dialog)
		font = QtGui.QFont()
		font.setFamily("黑体")
		font.setPointSize(20)
		self.lineEdit_id.setFont(font)
		self.lineEdit_id.setReadOnly(True)
		self.lineEdit_id.setObjectName("lineEdit_id")
		self.formLayout.setWidget(
			2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_id)
		self.verticalLayout.addLayout(self.formLayout)
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		spacerItem = QtWidgets.QSpacerItem(
			40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
		self.horizontalLayout.addItem(spacerItem)
		self.pushButton = QtWidgets.QPushButton(Dialog)
		font = QtGui.QFont()
		font.setFamily("黑体")
		font.setPointSize(20)
		self.pushButton.setFont(font)
		self.pushButton.setObjectName("pushButton")
		self.horizontalLayout.addWidget(self.pushButton)
		self.verticalLayout.addLayout(self.horizontalLayout)

		self.retranslateUi(Dialog)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
		self.label.setText(_translate("Dialog", "MAC:"))
		self.label_2.setText(_translate("Dialog", "硬盘序列号："))
		self.label_3.setText(_translate("Dialog", "软件注册序列号"))
		self.pushButton.setText(_translate("Dialog", "确定"))






class NetClick(QProgressDialog):

	def __init__(self,diskId,macid,deviceId,apiUrl=r"http://api.commaai.xin"):
		QProgressDialog.__init__(self,"正在联网校验，请稍后。",'cancel',0,100)
		self._diskid = diskId
		self._macid = macid
		time.sleep(3)
		self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
		self.setWindowTitle("联网校验")
		self.resize(500,100)
		self.setMaximumSize(500,100)
		self.setMinimumSize(500,100)
		self.url = apiUrl+ r'/software/get_oauth_sign'
		
		tim = str(int(datetime.now().timestamp()))
		self.dic = {"device_id":deviceId,
			"disk_id":diskId,
			"mac_id":macid,
			"client_time":tim,
			"utm_medium":"api",
			"utm_source":"comma_api",
		}
	
		self.api_sign = self.api_sign_hexdigest(self.dic)
		self.dic["api_sign"] = self.api_sign
		
	#联网认证
	def connectServer(self):
		self.setValue(50)         
		resp = requests.post(self.url, data=self.dic, timeout=3)
		if resp.status_code == 200:
			print(resp.text)
			dictget = json.loads(resp.text)
			if dictget["code"] != "200":
				self.reject()
			data = dictget["data"]
			deltime = int(data["valid_time"])
			if deltime < int(datetime.now().timestamp()):
				self.reject()
			self.ongetMD5.emit(data["oauth_sign"],str(data["valid_time"]))
			self.accept()
		else:
			self.reject()

	def showEvent(self,event):
		self.connectServer()

	def api_sign_hexdigest(self, dict):
		"""
		It is used to produce the digest of the information;
		The rule is specified in 'check_str';
		:param dict: the dictionary data which will be passed to the server;
		:return:
		"""
		ordered_dict = collections.OrderedDict(sorted(dict.items()))
		input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
		check_str = input + '&' + self.sign_key
		hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
		return hexdigest

	ongetMD5 = pyqtSignal(str,str)








class ClickMD5Dialog(QDialog, Ui_Dialog):

	def __init__(self,deviceId="cm002",apiUrl=r"http://api.commaai.xin"):
		QDialog.__init__(self, None)
		Ui_Dialog.__init__(self)
		self.setupUi(self)
		self.lineEdit_id.setReadOnly(False)
		self.diskID = getHardDiskId()
		self.mac = getMac()
		self.lineEdit_disk.setText(self.diskID)
		self.lineEdit_mac.setText(self.mac)
		self.pushButton.clicked.connect(self.__chickMd5)
		self.setWindowTitle("注册校验")
		self.valid_time = None
		self.deviceid = deviceId
		try:
			with open(r"sign.data", "rb") as f:
				b = f.read()[:-2]
				l = pickle.loads(b)
				self.__NetChickMd5(l[0],l[1])				
		except Exception as e:
			print("ERROR",e)
			t = NetClick(self.diskID,self.mac,deviceId,apiUrl)
			t.ongetMD5.connect(self.__NetChickMd5)
			if t.exec() == QDialog.Accepted:
				print("get data")
			else:
				print("get fail")
				self.reject()


	
	@pyqtSlot(str,str)
	def __NetChickMd5(self,stt,stime):
		self.md5_sign = stt
		self.valid_time = stime

		self.lineEdit_id.setText(stt)
		

		
	@pyqtSlot()
	def __chickMd5(self):
		md = getDevMd5(self.deviceid,self.diskID,self.mac,self.valid_time)
		print(md)
		if self.lineEdit_id.text() == md:
			lis = [self.md5_sign,self.valid_time]
			with open(r"sign.data", "wb") as f:
				f.write(pickle.dumps(lis)+b'\xff\aa')
			self.accept()
		else:
			self.reject()

	
	def api_sign_hexdigest(self, dict):
		"""
		It is used to produce the digest of the information;
		The rule is specified in 'check_str';
		:param dict: the dictionary data which will be passed to the server;
		:return:
		"""
		ordered_dict = collections.OrderedDict(sorted(dict.items()))
        # print('ordered_dict', ordered_dict)

		input = '&'.join([key + '=' + str(value) for (key, value) in ordered_dict.items() if key != 'api_sign'])
        # print('input', input)

		check_str = input + '&' + self.sign_key
        # print('check_str', check_str)

		hexdigest = hashlib.sha256(check_str.encode()).hexdigest()
        # print('hexdigest', hexdigest)

		return hexdigest




class GeneratingMD5Dialog(QDialog, Ui_Dialog):

	def __init__(self):
		QDialog.__init__(self, None)
		Ui_Dialog.__init__(self)
		self.setupUi(self)
		self.lineEdit_disk.setReadOnly(False)
		self.lineEdit_mac.setReadOnly(False)
		self.diskID = getHardDiskId()
		self.mac = getMac()
		self.lineEdit_disk.setText(self.diskID)
		self.lineEdit_mac.setText(self.mac)
		self.pushButton.clicked.connect(self.__getMd5)
		self.setWindowTitle("注册机")

	@pyqtSlot()
	def __getMd5(self):
		md = getDevMd5(self.diskID, self.mac)
		self.lineEdit_id.setText(md)



if __name__=="__main__":
	app = QApplication(sys.argv)
	de = ClickMD5Dialog()
	if de.exec() == QDialog.Accepted:
		print("oauth_sign Success!!!!")
	else:
		print("oauth_sign Fail!!!!")

	#print(getDevMd5("cm002","EJ76N501311206G01   _00000001.","60:14:B3:6D:5F:AB","1609343999"))
	#print("ddeeb7a55c7e51886bee4f0665e3d1aa82db87b6f6c55c54e5a0462474357adb")
	
