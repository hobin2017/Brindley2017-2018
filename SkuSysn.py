import sys,os
import time
import requests
from datetime import datetime
import hashlib
from PyQt5.QtCore import pyqtSlot, pyqtSignal,QThread,QObject,QTimer
from PyQt5.QtWidgets import QApplication
import pymysql,collections,json


def delete_file_folder(src):
	'''delete files and folders'''

	if os.path.isfile(src):
		try:
			os.remove(src)
		except:
			pass
	elif os.path.isdir(src):
		for item in os.listdir(src):
			itemsrc=os.path.join(src,item)
			delete_file_folder(itemsrc) 
		try:
			pass
			#os.rmdir(src)
		except:
			pass




class SkuSysnServer(QThread):

	def __init__(self,dbHost="localhost",user="root",password="123456",dbname="storegoods",store_id='2',apiUrl=r"http://api.commaai.xin",parent=None):
		QThread.__init__(self)
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.timoutEvent)
		self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
		self.downingCount = 0
		self.downUrl = apiUrl+r'/offline/cv/sku_dwonload'
		self.finishUrl = apiUrl+r'/offline/cv/finish_dwonload'
		
		self.dbHost = dbHost
		self.dbUser = user
		self.dbPassword = password
		self.dbName = dbname
		self.store_id = store_id
		self.timer.start(1000*60*5)


	@pyqtSlot()
	def timoutEvent(self):
		print("timoutEvent:")
		self.downingCount = 0
		self.sysDBRequests()
		self.savePic()
		self.sysFinshSignal.emit()

	sysFinshSignal = pyqtSignal()

	#获取更新的商品数据
	def sysDBRequests(self):
		self.sign_key = '4b111cc14a33b88e37e2e2934f493458'
		self.dict = {"api_sign":None,
					   'count':'1',
					   'store_id': store_id,
						'utm_medium':'qt',
					   'utm_source':'box',
					   'client_time':str(int(datetime.now().timestamp()))
					   }
		self.dict['api_sign'] = self.api_sign_hexdigest(self.dict)
		print("sysDBRequests",self.dict['api_sign'])
		resp01 = requests.post(self.downUrl, data=self.dict, timeout=3)
		if resp01.status_code == 200:
			self.dictget = json.loads(resp01.text)["data"]
			self.HanderRequests(self.dictget)
		else:
			print("sysfail!!")

	def is_jpg(self,data):  
		data = data[:11]
		
		if data[:4] != b'\xff\xd8\xff\xe0' and data[:4]!=b'\xff\xd8\xff\xe1':   
			return False
		if data[6:] != b'JFIF\0' and data[6:] != b'Exif\0':
			return False
		return True

	#保存图片到本地
	def savePic(self):
		db = pymysql.connect(self.dbHost,self.dbUser,self.dbPassword,self.dbName,charset='utf8')

		cursor = db.cursor()
		sqldel = "SELECT sku_id,picture FROM storegoods"
		try:
			cursor.execute(sqldel)
			db.commit()
			results = cursor.fetchall()
			delete_file_folder("skuPic/")
			if os.path.exists('skuPic') == False:
				os.mkdir('skuPic')
			for row in results:
				if row[1]==None or (not self.is_jpg(row[1])):
					continue
				with open("skuPic/"+str(row[0])+".jpg","wb") as fd:
					fd.write(row[1])

		except Exception as e:
			db.rollback()
			print("SQL ERROR : ",e)
		db.close()

	#处理查询到的request
	def HanderRequests(self,jsonObject):
		changeCount = jsonObject["total_record"]
		if changeCount==0:
			print("Dont need to update") 
			return
		dataList = jsonObject["list"] 
		lisNumber = len(dataList)
		self.downingCount += lisNumber
		sku_ids = ""
		for data in dataList:
			self.HanderSql(data)
			sku_ids+=str(data["sku_id"])+','

		self.downloadPictures()
		sku_ids = sku_ids[:-1]
		sendData = {"api_sign":None,
					   'count':'1',
					   'store_id': store_id,
					   'utm_medium':'qt',
					   'utm_source':'box',
					   'client_time':str(int(datetime.now().timestamp())),
					   'sku_ids':sku_ids
					   }
		sendData['api_sign'] = self.api_sign_hexdigest(sendData)
		resp = requests.post(self.finishUrl, data=sendData, timeout=3)
		if resp.status_code == 200:
			print("updata success")
		else:
			pass
		if changeCount!=self.downingCount:
			self.sysDBRequests()

	#向数据库插入数据
	def HanderSql(self,data):
		
		db = pymysql.connect(self.dbHost,self.dbUser,self.dbPassword,self.dbName,charset='utf8')

		cursor = db.cursor()

		sqldel = "delete from storegoods where cv_id = '%s'"%data["cv_id"]
		sql = "insert into storegoods(cv_id,sku_id,sku_price,sku_code,goods_id,sku_name,bar_code,goods_spec," +\
								"goods_image,goods_weight,packing_num,packing_units,down_time,goods_name,store_id) " +\
									"Values ('%s','%s','%s','%s','%s','%s','%s','%s','%s'," +\
									"'%s','%s','%s','%s','%s','%s')"
		
		sql = sql%(data["cv_id"],data["sku_id"],data["sku_price"],data["sku_code"],data["goods_id"]\
					,data["sku_name"],data["bar_code"],data["goods_spec"],data["goods_image"],data["goods_weight"]\
					,data["packing_num"],data["packing_units"],datetime.now().strftime('%Y-%m-%d %H:%M:%S')\
					,data["goods_name"],self.store_id)
		try:
			cursor.execute(sqldel)
			db.commit()

			cursor.execute(sql)
			db.commit()
		except Exception as e:
			db.rollback()
			print("SQL ERROR : ",e)
		db.close()

	#下载图片到数据库
	def downloadPictures(self):
		db = pymysql.connect(self.dbHost,self.dbUser,self.dbPassword,self.dbName,charset='utf8')
		#db = mysqlc.connect(host="192.168.222.132",port=3306,user='root',password='123456',database='storegoods',charset='utf8')

		cursor = db.cursor()
		findNeedToUpdata = "select id,goods_image,sku_id from storegoods where picture is null and goods_image <> ''"

		try:
			row  = cursor.execute(findNeedToUpdata)
			results = cursor.fetchall()
			head = {"Accept":"application/octet-stream"}
			print("row : ",row,len(results))
			if row<1:
				print("Dont need to download pictures")
				return
			for row in results:
				id = row[0]
				imgUrl = row[1]
				r = requests.get(imgUrl, stream=True,headers=head)
				picData =  r.raw.read()

				ss = {'pic':picData,'id':id}
				imgSql = "Update storegoods set picture=%(pic)s where id='%(id)s' "
				cursor.execute(imgSql,ss)
				db.commit()

		except Exception as e:
			print("SQL ERROR : ",e)
		db.commit()
		db.close()


		
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



if __name__=="__main__":
	app = QApplication(sys.argv)
	t = SkuSysnServer(dbHost="192.168.20.168")
	t.timoutEvent()

	#sys.exit(app.exec_())





