# -*- coding=utf-8 -*-

from PyQt5.QtSerialPort import QSerialPort,QSerialPortInfo
from PyQt5.QtCore import QIODevice,QObject, pyqtSlot,pyqtSignal,QByteArray,Qt,QThread
from functools import wraps
import struct

import  threading

def singleton(cls):
    instances = {}
    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return getinstance

def byteToInt(strbyte):
    if type(strbyte)==str:
        strbyte = strbyte.encode('UTF-8')
    tt = strbyte + b'\x00'
    i = struct.unpack("<h",tt)[0]
    return i

def get_char_bit(char,n):
    return (char >> (8-n)) & 1

#get the LRC
def getLRC(cmd):
    tmp = cmd[1]+cmd[2]+cmd[3]
    if(get_char_bit(tmp,1)==1):
        tmp = ~tmp
    tmp = struct.pack('<h', tmp)[0] + 1
    return tmp

#add LRC to Cmd
def addLRC(cmd):
    cmd[4] = getLRC(cmd)
    return cmd

def checkLRC(cmd):
    if type(cmd) == QByteArray:
        cmd = cmd.data()
    if type(cmd) != bytearray:
        cmd = bytearray(cmd)
    return cmd[4]==getLRC(cmd)



@singleton
class SerialPortConsole(QSerialPort):

    templet = b'\x3a\x00\x00\x00\x00\x0d\x0a'

    # int is id of door
    degaussSuccess = pyqtSignal(int)
    inOpenDoorSuccess = pyqtSignal(int)
    outOpenDooSuccess = pyqtSignal(int)
    outOpenDooSuccessByUser = pyqtSignal(int)


    def __init__(self,serial=None,parent=None):
        super().__init__()
        i =  QSerialPortInfo.availablePorts()
        if len(i)==0:
            print("Error:Get Serial Port Fail!!")
            return None
        if serial == None:
            self.setPort(i[0])
            self.info = i[0]
            print("Serial Port:"+i[0].description())

        self.setBaudRate(115200)
        self.setDataBits(QSerialPort.Data8)
        self.setStopBits(QSerialPort.OneStop)
        if not self.open(QIODevice.ReadWrite):
            print("Error:Open %s Fail"%i[0].portName())
            return None
        self.setDataTerminalReady(True)
        self.readyRead.connect(self.acceptData,type=Qt.QueuedConnection)
        self.data = QByteArray()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        #print("init finash!!!")
    


    #send data
    @pyqtSlot(int)
    def sendOpenDoorIn(self,doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = byteToInt(b'\xCC')
        if self.write(addLRC(cmd)) == 7:
            return True
        else:
            return False
    
    @pyqtSlot(int)
    def sendOpenDoorOut(self,doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = byteToInt(b'\xBB')
        if self.write(addLRC(cmd)) == 7:
            return True
        else:
            return False

    @pyqtSlot(int)
    def sendDegauss(self,doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = byteToInt(b'\xAA')
        end = addLRC(cmd)
        if self.write(end) == 7:
            return True
        else:
            return False

    @pyqtSlot()
    def acceptData(self):
        print("get data from "+self.info.description())
        self.data.append(self.readAll()) # read all data
        while self.data.length()>0:      
            if self.data.length()>=7:    # if get a complete data
                for i in range(self.data.length()):
                    if self.data[i]=='\x3a':        # find the SOI
                        tmp = self.data[i:7]        # get a cmd
                        print("get cmd :",tmp.data())
                        tmp = bytearray(tmp.data())
                        self.data = self.data[i+7:]  #cut data
                        doorNumber = tmp[1]
                        if checkLRC(tmp):      #check LRC
                            if tmp[2]==byteToInt(b'\xaa'):
                                self.degaussSuccess.emit(doorNumber)
                            elif tmp[2]==byteToInt(b'\xbb'):
                                if tmp[3]==byteToInt(b'\x01'):
                                    self.outOpenDooSuccess.emit(doorNumber)
                                elif tmp[3]==byteToInt(b'\x02'):
                                    self.outOpenDooSuccessByUser.emit(doorNumber)
                            elif tmp[2]==byteToInt(b'\xcc'):
                                self.inOpenDoorSuccess.emit(doorNumber)
                        else:
                            print("LRC check fail!!")
                        break
            self.data.append(self.readAll())
        print("accept Data finish.")



if __name__ == '__main__':
    from PyQt5.QtGui import QGuiApplication
    
    app = QGuiApplication([])
    s = SerialPortConsole()
    s.sendDegauss(1)
    
    #app.exec_()

    