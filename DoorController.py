# -*- coding: utf-8 -*-
"""
QSerialPort.readAll():
   Reads all remaining data and returns it as a QByteArray class. Returning an empty QByteArray can mean either that
no data was currently available for reading, or that an error occurred.
"""
import logging

from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QByteArray, QObject, QIODevice
import struct
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from LoggingModule import MyLogging1


class DoorController01(QObject):
    """
    This class will communicates with the arm chip by using serial port;
    This class is modified based on my workmate's work(ZiJie);
    """
    degaussSuccess = pyqtSignal(int)  # door number
    inOpenDoorSuccess = pyqtSignal(int)  # door number
    outOpenDooSuccess = pyqtSignal(int)  # door number
    outOpenDooSuccessByUser = pyqtSignal(int)  # door number

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='115200',
                 data_bits='8', stop_bits='1',**kwargs):
        super().__init__()
        self.templet = b'\x3a\x00\x00\x00\x00\x0d\x0a'
        self.expected_command_length = 7
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData)

        # some variables
        self.parent = parent
        self.data = QByteArray()
        self.mylogger1_door_controller = logging.getLogger(logger_name)

        if not self.serial.open(QIODevice.ReadWrite):
            self.mylogger1_door_controller.error("Opening serial port fails in the initialization of DoorController01")
            sys.exit('Opening serial port fails in the initialization of DoorController01')
        self.mylogger1_door_controller.info('The initialization of DoorController01 is successful.')


    def calculate_LRC(self, cmd):
        """
        the [] operation of bytes object will convert bytes into int.
        :param cmd: expected length is 7.
        :return:
        """
        lrc01 = ~(cmd[1] + cmd[2] + cmd[3]) + 1  # int
        lrc02 = struct.pack('>h', lrc01)  # 2 bytes since python int has 2 bytes
        return lrc02[1]

    def acceptData(self):
        self.mylogger1_door_controller.info("acceptData of DoorController01 class starts.")
        self.data.append(self.serial.readAll()) # self.data is the QByteArray class (not list).
        self.mylogger1_door_controller.info('current buffer with length %s is %s'
                                            %(self.data.length(), self.data.data()))
        # print(type(self.data.data()))  # <class 'bytes'>
        try:
            # process data
            complete_command_status = False
            index_soi = 0
            for index in range(self.data.length()):
                # to find the SOI. '\x3a' is  ':' in ASCII table.
                if self.data[index] == '\x3a':
                    self.mylogger1_door_controller.info('finding the SOI successfully')
                    temp_qbytearray = self.data[index:index + self.expected_command_length]  # <class 'PyQt5.QtCore.QByteArray'>
                    if len(temp_qbytearray) == 7:
                        # Assignment operation of temp_bytes is required and hence bytearray() is used.
                        temp_bytes = bytearray(temp_qbytearray.data())
                        self.mylogger1_door_controller.info("the data is complete with %s:" % temp_bytes)
                        doorNumber = temp_bytes[1]  # int, unsigned int
                        if temp_bytes[4] == self.calculate_LRC(temp_bytes):
                            if temp_bytes[2] == b'\xaa'[0]:
                                self.mylogger1_door_controller.info('sending degaussSuccess signal')
                                self.degaussSuccess.emit(doorNumber)
                            elif temp_bytes[2] == b'\xbb'[0]:
                                if temp_bytes[3] == b'\x01'[0]:
                                    self.mylogger1_door_controller.info('sending outOpenDooSuccess signal')
                                    self.outOpenDooSuccess.emit(doorNumber)
                                elif temp_bytes[3] == b'\x02'[0]:
                                    self.mylogger1_door_controller.info('sending outOpenDooSuccessByUser signal')
                                    self.outOpenDooSuccessByUser.emit(doorNumber)
                            elif temp_bytes[2] == b'\xcc'[0]:
                                self.mylogger1_door_controller.info('sending inOpenDoorSuccess signal')
                                self.inOpenDoorSuccess.emit(doorNumber)
                            else:
                                self.mylogger1_door_controller.info('sending no signal')
                        else:
                            self.mylogger1_door_controller.info("checking LRC fails and discard such command.")
                        complete_command_status = True
                    else:
                        self.mylogger1_door_controller.info('the data is not complete.')
                    break
                else:
                    index_soi = index + 1

            # to cut data after processing
            if complete_command_status:
                self.data = self.data[index_soi + self.expected_command_length:]
            else:
                self.data = self.data[index_soi:]
            self.mylogger1_door_controller.info('After cutting, the buffer is %s' % self.data.data())

            # Since the clock frequency of main process is faster than the clock frequency of MCU, the below
            # operation can added to ensure it processes the newest data at next time.
            if self.data.length() >= 14:
                self.mylogger1_door_controller.info('clearing the buffer since there are too much data')
                self.data.clear()
        except BaseException:
            self.mylogger1_door_controller.error('***------------------------Be careful! Error occurs in DoorController01!------------------------***', exc_info=True)
        self.mylogger1_door_controller.info("acceptData of DoorController01 class ends.")

    def sendOpenDoorIn(self, doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = b'\xCC'[0]
        cmd[4] = self.calculate_LRC(cmd)
        if self.serial.write(cmd) == 7:
            return True
        else:
            return False

    def sendOpenDoorOut(self, doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = b'\xBB'[0]
        cmd[4] = self.calculate_LRC(cmd)
        if self.serial.write(cmd) == 7:
            return True
        else:
            return False

    def sendDegauss(self, doorNumber):
        cmd = bytearray(self.templet)
        cmd[1] = struct.pack('<h', doorNumber)[0]
        cmd[2] = b'\xAA'[0]
        cmd[4] = self.calculate_LRC(cmd)
        if self.serial.write(cmd) == 7:
            return True
        else:
            return False


class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.door_controller = DoorController01(port_name='COM3')

    def closeEvent(self, *args, **kwargs):
        self.door_controller.serial.close()
        super().closeEvent(*args, **kwargs)


if __name__ == '__main__':
    mylogging = MyLogging1(logger_name='hobin')
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    sys.exit(app.exec_())

