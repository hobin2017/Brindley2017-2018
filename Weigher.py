# -*- coding: utf-8 -*-
"""
In[1]: b'\x0d'.decode('ascii')
Out[1]: '\r'

Some non-printable bytes is represented from b'\x80' to b'\xFF'.
"""
import logging
import sys
from PyQt5.QtCore import QObject, QIODevice, Qt, pyqtSignal, QByteArray, QTimer
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QApplication, QFrame

from LoggingModule import MyLogging1


class Weigher1(QObject):
    """
    This class communicates with the weigher. The weigher will send data probably 3 times every second.
    """
    empty = pyqtSignal()
    detect_changed = pyqtSignal(object)
    # detect_minus = pyqtSignal(object)
    # detect_plus = pyqtSignal(object)

    def __init__(self, port_name, parent = None,*, baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher1, self).__init__()
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name) # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData1)
        # self.serial.readyRead.connect(self.acceptData1, type=Qt.QueuedConnection)
        # self.serial.bytesWritten.connect(self.acceptData2)

        if self.serial.open(QIODevice.ReadOnly):
            # self.serial.setDataTerminalReady(True)  # setting the specific pin to the high-value voltage;
            print('The connection to the serial port is successful.')
        else:
            print('The connection to the serial port is failed.')


    def acceptData1(self):
        """
        This function will be executed when the new data arrive on the serial port;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii') # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.current_data = float(data2[1:-4])  # the value part of the original string;
        # print('The editted part of data is %s' %self.current_data)

        if self.current_data > 2:
            if self.last_data == self.current_data:
                # if true, the weigher must send two successive same data.
                # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2:
                    print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.record_value = self.current_data
                    self.serial.close()
                    self.detect_changed.emit(self.current_data)
                else:
                    print('Weigher says that the record value is the same as the current data.')

            else:
                self.last_data = self.current_data  # refreshing the value of last data.
        else:
            # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
            # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
            if self.record_value >2:
                print('Weigher detects significant change %s to zero.' % self.record_value)
                self.record_value = self.current_data
                self.empty.emit()
            else:
                print('Weigher detects nothing with %s.' % self.current_data)
        discard = self.serial.readAll()


class Weigher1_1(QObject):
    """
    This class communicates with the weigher. The weigher will send data probably 3 times every second.
    Compared with the Weigher1 class, this module starts after all initializations are finished.
    Compared with the Weigher1 class, the logging module is introduced to this module.
    Compared with the Weigher2 class, the logic part is changed. the detect_plus signal is emitted only if the self.record_value increase.
    """
    empty = pyqtSignal()
    detect_plus = pyqtSignal(object)

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher1_1, self).__init__()
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData1)
        # self.serial.readyRead.connect(self.acceptData1, type=Qt.QueuedConnection)
        # self.serial.bytesWritten.connect(self.acceptData2)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.mylogger1_1weigher = logging.getLogger(logger_name)
        self.mylogger1_1weigher.info('The initialization of Weigher1_1 is successful.')


    def acceptData1(self):
        """
        This function will be executed when the new data arrive on the serial port;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii') # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.current_data = float(data2[1:-4])  # the value part of the original string;
        # print('The editted part of data is %s' %self.current_data)

        if self.current_data > 2:
            if self.last_data == self.current_data:
                # if true, the weigher must send two successive same data.
                # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                if self.record_value + 2 < self.current_data:
                    # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.mylogger1_1weigher.info('Weigher1_1 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.record_value = self.current_data
                    self.serial.close()
                    self.detect_plus.emit(self.current_data)
                elif self.current_data < self.record_value - 2:
                    self.mylogger1_1weigher.info('Weigher1_1 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.record_value = self.current_data
                else:
                    # print('Weigher says that the record value is the same as the current data.')
                    self.mylogger1_1weigher.debug('Weigher1_1 says that the record value is the same as the current data.')
            else:
                self.last_data = self.current_data  # refreshing the value of last data.
        else:
            # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
            # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
            if self.record_value >2:
                # print('Weigher detects significant change %s to zero.' % self.record_value)
                self.mylogger1_1weigher.info('Weigher1_1 detects significant change %s to zero.' % self.record_value)
                self.record_value = self.current_data
                self.empty.emit()
            else:
                # print('Weigher detects nothing with %s.' % self.current_data)
                # self.mylogger1_1weigher.debug('Weigher1_1 detects nothing with %s.' % self.current_data)
                pass
        discard = self.serial.readAll()


class Weigher2(QObject):
    """
    This class communicates with the weigher. The weigher will send data probably 3 times every second.
    Compared with the Weigher1 class, this module starts after all initializations are finished.
    Compared with the Weigher1 class, the logging module is introduced to this module.
    """
    empty = pyqtSignal()
    detect_changed = pyqtSignal(object)

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher2, self).__init__()
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData1)
        # self.serial.readyRead.connect(self.acceptData1, type=Qt.QueuedConnection)
        # self.serial.bytesWritten.connect(self.acceptData2)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.mylogger2_weigher = logging.getLogger(logger_name)
        self.mylogger2_weigher.info('The initialization of Weigher2 is successful.')


    def acceptData1(self):
        """
        This function will be executed when the new data arrive on the serial port;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii') # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.current_data = float(data2[1:-4])  # the value part of the original string;
        # print('The editted part of data is %s' %self.current_data)

        if self.current_data > 2:
            if self.last_data == self.current_data:
                # if true, the weigher must send two successive same data.
                # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2:
                    # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.mylogger2_weigher.info('Weigher2 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.record_value = self.current_data
                    self.serial.close()
                    self.detect_changed.emit(self.current_data)
                else:
                    # print('Weigher says that the record value is the same as the current data.')
                    # self.mylogger2_weigher.debug('Weigher2 says that the record value is the same as the current data.')
                    pass
            else:
                self.last_data = self.current_data  # refreshing the value of last data.
        else:
            # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
            # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
            if self.record_value >2:
                # print('Weigher detects significant change %s to zero.' % self.record_value)
                self.mylogger2_weigher.info('Weigher2 detects significant change %s to zero.' % self.record_value)
                self.record_value = self.current_data
                self.empty.emit()
            else:
                # print('Weigher detects nothing with %s.' % self.current_data)
                self.mylogger2_weigher.debug('Weigher2 detects nothing with %s.' % self.current_data)
        discard = self.serial.readAll()


class Weigher2_1(QObject):
    """
    This class communicates with the weigher. The weigher will send data probably 3 times every second.
    Compared with the Weigher1 class, this module starts after all initializations are finished.
    Compared with the Weigher1 class, the logging module is introduced to this module.
    Compared with the Weigher2 class, the main difference is that the self.wave_status is added in the logical part;
    """
    empty = pyqtSignal()
    detect_changed = pyqtSignal(object)

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher2_1, self).__init__()
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData1)
        # self.serial.readyRead.connect(self.acceptData1, type=Qt.QueuedConnection)
        # self.serial.bytesWritten.connect(self.acceptData2)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.wave_status = False
        self.mylogger2_1weigher = logging.getLogger(logger_name)
        self.mylogger2_1weigher.info('The initialization of Weigher2_1 is successful.')


    def acceptData1(self):
        """
        This function will be executed when the new data arrive on the serial port;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
        data2 = data1.data().decode('ascii') # converting the data type to str (the original string);
        # print('The length of data is %s and the value part is %s' %(len(data2), data2))
        self.current_data = float(data2[1:-4])  # the value part of the original string;
        # print('The editted part of data is %s' %self.current_data)

        if self.current_data > 2:
            if self.last_data == self.current_data:
                # if true, the weigher must send two successive same data.
                # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2 or self.wave_status:
                    # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.mylogger2_1weigher.info('Weigher2_1 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                    self.record_value = self.current_data
                    self.wave_status = False
                    self.serial.close()
                    self.detect_changed.emit(self.current_data)
                else:
                    # print('Weigher says that the record value is the same as the current data.')
                    # self.mylogger2_1weigher.debug('Weigher2_1 says that the record value is the same as the current data.')
                    pass
            else:
                self.last_data = self.current_data  # refreshing the value of last data.
                self.wave_status = True
        else:
            # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
            # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
            if self.record_value >2:
                # print('Weigher detects significant change %s to zero.' % self.record_value)
                self.mylogger2_1weigher.info('Weigher2_1 detects significant change %s to zero.' % self.record_value)
                self.record_value = self.current_data
                self.empty.emit()
            else:
                # print('Weigher detects nothing with %s.' % self.current_data)
                self.mylogger2_1weigher.debug('Weigher2_1 detects nothing with %s.' % self.current_data)
        discard = self.serial.readAll()


class Weigher3(QObject):
    """
    This class communicates with the weigher. The weigher will send data probably 3 times every second.
    Compared withe the Weigher2_1 and the Weigher1_1 class, this class is the combination of them;
    Another difference is that it disconnect itself after the detect_changed or detect_plus is emitted;
    """
    empty = pyqtSignal()
    detect_changed = pyqtSignal(object)
    detect_plus = pyqtSignal(object)

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher3, self).__init__()
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData_standby)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.wave_status = False
        self.mylogger3_weigher = logging.getLogger(logger_name)
        self.mylogger3_weigher.info('The initialization of Weigher3 is successful.')


    def acceptData_standby(self):
        """
        This function will be executed when the new data arrive on the serial port;
        This slot will be connected with the readyRead signal of the QSerialPort object;
        This function does not emit the empty signal anymore!
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            # print('The length of data is %s and the value part is %s' %(len(data2), data2))
            try:
                self.current_data = float(data2[1:-4])  # the value part of the original string;
                # print('The editted part of data is %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_standby and force it to be the last data.')

            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger3_weigher.info(
                            'Weigher3 says there is significant change in acceptData_standby from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.serial.readyRead.disconnect(self.acceptData_standby)
                        self.detect_plus.emit(self.current_data)
                    elif self.current_data < self.record_value - 2:
                        self.mylogger3_weigher.info(
                            'Weigher3 says there is significant change in acceptData_standby from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger3_weigher.debug('Weigher1_1 says that the record value is the same as the current data.')
                        pass
                else:
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger3_weigher.info(
                        'Weigher3 detects significant in acceptData_standby change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    # self.mylogger3_weigher.debug('Weigher1_1 detects nothing with %s.' % self.current_data)
                    pass
            discard = self.serial.readAll()
        else:
            pass


    def acceptData_order(self):
        """
        This function will be executed when the new data arrive on the serial port;
        This slot will be connected with the readyRead signal of the QSerialPort object;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            # print('The length of data is %s and the value part is %s' %(len(data2), data2))
            try:
                self.current_data = float(data2[1:-4])  # the value part of the original string;
                # print('The editted part of data is %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_order and force it to be the last data.')

            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2 or self.wave_status:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger3_weigher.info('Weigher3 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.wave_status = False
                        self.serial.readyRead.disconnect(self.acceptData_order)
                        self.detect_changed.emit(self.current_data)
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger3_weigher.debug('Weigher3 says that the record value is the same as the current data.')
                        pass
                else:
                    self.last_data = self.current_data  # refreshing the value of last data.
                    if not self.wave_status:
                        self.wave_status = True
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger3_weigher.info('Weigher3 detects significant change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                    self.empty.emit()
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    self.mylogger3_weigher.debug('Weigher3 detects nothing with %s.' % self.current_data)
            discard = self.serial.readAll()
        else:
            pass


class Weigher3_1(QObject):
    """
    This class communicates with the weigher. The weigher will send data probably 3 times every second.
    Compared with the Weigher2_1 and the Weigher1_1 class, this class is the combination of them;
    Another difference is that it disconnect itself after the detect_changed or detect_plus is emitted;
    Compared with the Weigher3 class, it receives the float data with unit kg and convert it into g after successful conversion;;
    another difference is that self.wave_status = True when self.last_data + 3 < self.current_data or self.current_data < self.last_data - 3;
    """
    empty = pyqtSignal()
    to_standby = pyqtSignal()
    detect_changed = pyqtSignal(object)
    detect_plus = pyqtSignal(object)

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher3_1, self).__init__()
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData_standby)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.wave_status = False
        self.mylogger3_1weigher = logging.getLogger(logger_name)
        self.mylogger3_1weigher.info('The initialization of Weigher3_1 is successful.')


    def acceptData_standby(self):
        """
        This function will be executed when the new data arrive on the serial port;
        This slot will be connected with the readyRead signal of the QSerialPort object;
        This function does not emit the empty signal anymore!
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            # print('The length of data is %s and the value part is %s' %(len(data2), data2))
            try:
                self.current_data = float(data2[1:-4]) * 1000  # the value part of the original string;
                # print('The editted part of data is %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_1weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_standby and force it to be the last data.')

            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger3_1weigher.info('Weigher3_1 says there is significant change in acceptData_standby from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.serial.readyRead.disconnect(self.acceptData_standby)
                        self.detect_plus.emit(self.current_data)
                    elif self.current_data < self.record_value - 2:
                        self.mylogger3_1weigher.info('Weigher3_1 says there is significant change in acceptData_standby from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger3_1weigher.debug('Weigher1_1 says that the record value is the same as the current data.')
                        pass
                else:
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger3_1weigher.info('Weigher3_1 detects significant in acceptData_standby change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    # self.mylogger3_1weigher.debug('Weigher1_1 detects nothing with %s.' % self.current_data)
                    pass
            discard = self.serial.readAll()
        else:
            pass


    def acceptData_order(self):
        """
        This function will be executed when the new data arrive on the serial port;
        This slot will be connected with the readyRead signal of the QSerialPort object;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            # print('The length of data is %s and the value part is %s' %(len(data2), data2))
            try:
                self.current_data = float(data2[1:-4]) * 1000  # the value part of the original string;
                # print('The editted part of data is %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_1weigher.error('Cannot convert the data given by the weigher in acceptData_order and force it to be the last data.')

            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2 or self.wave_status:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger3_1weigher.info('Weigher3_1 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.wave_status = False
                        self.serial.readyRead.disconnect(self.acceptData_order)
                        self.detect_changed.emit(self.current_data)
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger3_1weigher.debug('Weigher3_1 says that the record value is the same as the current data.')
                        pass
                else:
                    if self.last_data + 3 < self.current_data or self.current_data < self.last_data - 3:
                        self.wave_status = True
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger3_1weigher.info('Weigher3_1 detects significant change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                    self.empty.emit()
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    self.mylogger3_1weigher.debug('Weigher3_1 detects nothing with %s.' % self.current_data)
            discard = self.serial.readAll()
        else:
            pass


    def acceptData_back_to_standby(self):
        """
        To accelerate the process which is back to the standby layout;
        """
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            try:
                self.current_data = float(data2[1:-4]) * 1000  # the value part of the original string;
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_1weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_standby and force it to be the last data.')
            if self.last_data + 2 < self.current_data or self.current_data < self.last_data - 2:
                self.serial.readyRead.disconnect(self.acceptData_back_to_standby)
                self.to_standby.emit()


class Weigher3_2(QObject):
    """
    Compared with Weigher3_1 class, the unit of the weigher is gramme.
    """
    empty = pyqtSignal()
    to_standby = pyqtSignal()
    detect_changed = pyqtSignal(object)
    detect_plus = pyqtSignal(object)

    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600', data_bits='8', stop_bits='1',**kwargs):
        """
        :param serial_port: for example, 'COM3'.
        :param parent:
        """
        super(Weigher3_2, self).__init__()
        # the setting about the QSerialPort;
        # list_serialPort = QSerialPortInfo.availablePorts()  # returns a list of the PyQt5.QtSerialPort.QSerialPortInfo class
        # for port in list_serialPort:
        #     print(port.portName())
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.acceptData_standby)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.wave_status = False
        self.mylogger3_2weigher = logging.getLogger(logger_name)
        self.mylogger3_2weigher.info('The initialization of Weigher3_2 is successful.')


    def acceptData_standby(self):
        """
        This function will be executed when the new data arrive on the serial port;
        This slot will be connected with the readyRead signal of the QSerialPort object;
        This function does not emit the empty signal anymore!
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            # print('The length of data is %s and the value part is %s' %(len(data2), data2))
            try:
                self.current_data = float(data2[1:-4])  # the value part of the original string;
                # print('The editted part of data is %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_2weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_standby and force it to be the last data.')

            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger3_2weigher.info('Weigher3_2 says there is significant change in acceptData_standby from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.serial.readyRead.disconnect(self.acceptData_standby)
                        self.detect_plus.emit(self.current_data)
                    elif self.current_data < self.record_value - 2:
                        self.mylogger3_2weigher.info('Weigher3_2 says there is significant change in acceptData_standby from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger3_2weigher.debug('Weigher1_1 says that the record value is the same as the current data.')
                        pass
                else:
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger3_2weigher.info('Weigher3_2 detects significant in acceptData_standby change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    # self.mylogger3_2weigher.debug('Weigher1_1 detects nothing with %s.' % self.current_data)
                    pass
            discard = self.serial.readAll()
        else:
            pass


    def acceptData_order(self):
        """
        This function will be executed when the new data arrive on the serial port;
        This slot will be connected with the readyRead signal of the QSerialPort object;
        the fixed length of the original string is 13;
        In string format, it looks like this '+  0.123 kg \n'
        """
        # print('New data comes from serial port')
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            # print('The length of data is %s and the value part is %s' %(len(data2), data2))
            try:
                self.current_data = float(data2[1:-4])  # the value part of the original string;
                # print('The editted part of data is %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_2weigher.error('Cannot convert the data given by the weigher in acceptData_order and force it to be the last data.')

            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2 or self.wave_status:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger3_2weigher.info('Weigher3_2 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.wave_status = False
                        self.serial.readyRead.disconnect(self.acceptData_order)
                        self.detect_changed.emit(self.current_data)
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger3_2weigher.debug('Weigher3_2 says that the record value is the same as the current data.')
                        pass
                else:
                    if self.last_data + 3 < self.current_data or self.current_data < self.last_data - 3:
                        self.wave_status = True
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger3_2weigher.info('Weigher3_2 detects significant change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                    self.empty.emit()
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    self.mylogger3_2weigher.debug('Weigher3_2 detects nothing with %s.' % self.current_data)
            discard = self.serial.readAll()
        else:
            pass


    def acceptData_back_to_standby(self):
        """
        To accelerate the process which is back to the standby layout;
        """
        if self.serial.canReadLine():
            data1 = self.serial.readLine()  # the data type is the PyQt5.QtCore.QByteArray class;
            data2 = data1.data().decode('ascii')  # converting the data type to str (the original string);
            try:
                self.current_data = float(data2[1:-4])  # the value part of the original string;
            except BaseException:
                self.current_data = self.last_data
                self.mylogger3_2weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_standby and force it to be the last data.')
            if self.last_data + 2 < self.current_data or self.current_data < self.last_data - 2:
                self.serial.readyRead.disconnect(self.acceptData_back_to_standby)
                self.to_standby.emit()


class Weigher4_1(QObject):
    """
      This class communicates with the weigher. The weigher will send data probably 3 times every second.
      Compared with Weigher3_1, the data about the weight is stored in a buffer. Currently, QTimer is used to read the
    buffer and process it.
      The second feature is that the communication detection is firstly introduced into this class. If there is no new
    data in the buffer, the weigher is assumed to be unavailable and no_new_data_error is emitted. For instance,
    the power of the weigher is gone.
      The third feature is that QSerialPort.errorOccurred signal is used to detect error.
    """
    empty = pyqtSignal()
    to_standby = pyqtSignal()
    detect_changed = pyqtSignal(object)
    detect_plus = pyqtSignal(object)
    no_new_data_error = pyqtSignal()
    error = pyqtSignal()  # Currently, it is not emitted


    def __init__(self, parent = None, logger_name='hobin', *, port_name ='COM3', baud_rate='9600',
                 data_bits='8', stop_bits='1', **kwargs):
        super(Weigher4_1, self).__init__()
        # timer for serial port
        self.no_new_data_counter = 0
        self.buffer_processing_interval = 400  # the unit is ms
        self.no_new_data_boundary = int(10 * 1000 / self.buffer_processing_interval)  # no new data in the time interval
        self.serial_port_timer = QTimer(self)
        # self.serial_port_timer.setSingleShot(True)
        self.serial_port_timer.setSingleShot(False)
        self.serial_port_timer.setInterval(self.buffer_processing_interval)
        self.serial_port_timer.timeout.connect(self.acceptData_standby)

        # timer for reopening
        self.reopening_timer_interval = 5000   # unit is millisecond
        self.reopening_related_timer = QTimer(self)
        self.reopening_related_timer.setSingleShot(True)
        self.reopening_related_timer.timeout.connect(self.trying2reopen_serial_port)

        # serial port
        self.serial_port_error_dict = {
            '0': 'QSerialPort.NoError',
            '1': 'QSerialPort.DeviceNotFoundError',
            '2': 'QSerialPort.PermissionError',
            '3': 'QSerialPort.OpenError',
            '4': 'QSerialPort::ParityError',
            '5': 'QSerialPort.FramingError',
            '6': 'QSerialPort.BreakConditionError ',
            '7': 'QSerialPort.WriteError',
            '8': 'QSerialPort.ReadError',
            '9': 'QSerialPort.ResourceError ',
            '10': 'QSerialPort.UnsupportedOperationError',
            '11': 'QSerialPort.UnknownError',
            '12': 'QSerialPort.TimeoutError',
            '13': 'QSerialPort.NotOpenError'
        }
        self.serial_port_buffer = QByteArray()
        # self.new_data_arrival_counter = 0  # it is used in store2buffer function
        self.serial = QSerialPort()  # It is the subclass of the QIODevice class;
        self.serial.setPortName(port_name)  # passing name such as 'COM1'
        self.serial.setBaudRate(int(baud_rate))
        self.serial.setDataBits(QSerialPort.DataBits(int(data_bits)))
        self.serial.setStopBits(QSerialPort.StopBits(int(stop_bits)))
        self.serial.readyRead.connect(self.store2buffer)
        self.serial.errorOccurred.connect(self.handling_serial_port_error)

        # some variables
        self.parent = parent
        self.last_data = 0.0  # it represents the last data received from the weigher;
        self.current_data = 0.0  # it represents the current data received from the weigher;
        self.record_value = 0.0
        self.wave_status = False

        self.mylogger4_1weigher = logging.getLogger(logger_name)
        self.mylogger4_1weigher.info('The initialization of Weigher4_1 is successful.')


    def store2buffer(self):
        """
        storing the data into a buffer;
        :return:
        """
        # self.new_data_arrival_counter = self.new_data_arrival_counter + 1
        # if self.new_data_arrival_counter > 1000:
        #     self.new_data_arrival_counter = 0
        #     self.mylogger4_1weigher.info('Weigher4_1: store2buffer starts')
        if self.serial.canReadLine():
            self.serial_port_buffer.append(self.serial.readAll())
            # self.mylogger4_1weigher.info('Weigher4_1: the current size of the buffer is %s' % self.serial_port_buffer.length())

    def acceptData_standby(self):
        """
          This slot will be connected with the timeout signal of the QTimer object;
          The data part is extracted based on two different '\n'.
        """
        # you need to ensure there are different b'\n' in the buffer since the backward searching includes the start point
        current_data_end_index = self.serial_port_buffer.lastIndexOf(b'\n', -1)  # searching backward from the last one
        if current_data_end_index < 1:
            # current_data_end_index is equal to 0 or -1
            current_data_start_index = -1
        else:
            # Be careful that 'current_data_end_index=0' results in 'current_data_start_index=0'
            current_data_start_index = self.serial_port_buffer.lastIndexOf(b'\n', current_data_end_index - 1)
        # self.mylogger4_1weigher.debug('acceptData_standby: slicing [%s, %s]' %(current_data_start_index, current_data_end_index))

        if current_data_start_index == -1:
            # error detection
            self.no_new_data_counter = self.no_new_data_counter + 1
            if self.no_new_data_counter > self.no_new_data_boundary:
                self.mylogger4_1weigher.error(
                    'acceptData_standby in Weigher4_1: no weigher data for a while and self.no_new_data_counter is %s'
                                              % self.no_new_data_counter)
                self.no_new_data_counter = 1
                self.no_new_data_error.emit()
            else:
                self.mylogger4_1weigher.debug('acceptData_standby in Weigher4_1: self.no_new_data_counter is %s'
                                              % self.no_new_data_counter)
        else:
            self.no_new_data_counter = 0

            # step1: extracting data
            # At this time, the data ranging from current_data_start_index to current_data_end_index will be the data.
            data1 = self.serial_port_buffer[current_data_start_index: current_data_end_index]
            # self.mylogger4_1weigher.debug('acceptData_standby: %s' %data1)
            try:
                # without the strip, error happens in float() operation, such as invisible character
                data2 = str(data1, encoding='utf-8').strip()
                if current_data_start_index < 0 or current_data_end_index <0:
                    self.mylogger4_1weigher.debug('The length of data is %s and the value part is: %s' % (len(data2), data2))
                self.current_data = float(data2[1: -2]) * 1000
                # self.mylogger4_1weigher.debug('The edited part of data is: %s' %self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger4_1weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_standby and force it to be the last data.'
                    , exc_info=True)

            # step2: processing data
            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger4_1weigher.info(
                            'Weigher4_1 says there is significant change in acceptData_standby from %s to %s.' % (
                            self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.serial_port_timer.timeout.disconnect(self.acceptData_standby)
                        self.detect_plus.emit(self.current_data)
                    elif self.current_data < self.record_value - 2:
                        self.mylogger4_1weigher.info(
                            'Weigher4_1 says there is significant change in acceptData_standby from %s to %s.' % (
                            self.record_value, self.current_data))
                        self.record_value = self.current_data
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger4_1weigher.debug('Weigher1_1 says that the record value is the same as the current data.')
                        pass
                else:
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger4_1weigher.info(
                        'Weigher4_1 detects significant in acceptData_standby change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    # self.mylogger4_1weigher.debug('Weigher1_1 detects nothing with %s.' % self.current_data)
                    pass

            # step3: cleaning buffer
            # If the latest part cannot be converted to float successfully and no data is sent anymore, this will result
            # in the bug of detecting error. Therefore, I clean the buffer every time.
            discard = self.serial_port_buffer.remove(0, current_data_end_index)  # does not delete the right boundary

    def acceptData_order(self):
        """
        This slot will be connected with the timeout signal of the QTimer object;
        The data part is extracted based on two different '\n'.
        """
        # you need to ensure there are different b'\n' in the buffer since the backward searching includes the start point
        current_data_end_index = self.serial_port_buffer.lastIndexOf(b'\n', -1)  # searching backward from the last one
        if current_data_end_index < 1:
            # current_data_end_index is equal to 0 or -1
            current_data_start_index = -1
        else:
            # Be careful that 'current_data_end_index=0' results in 'current_data_start_index=0'
            current_data_start_index = self.serial_port_buffer.lastIndexOf(b'\n', current_data_end_index - 1)
        # self.mylogger4_1weigher.debug('acceptData_order: slicing [%s, %s]' % (current_data_start_index, current_data_end_index))

        if current_data_start_index == -1:
            # error detection
            self.no_new_data_counter = self.no_new_data_counter + 1
            if self.no_new_data_counter > self.no_new_data_boundary:
                self.mylogger4_1weigher.error(
                    'acceptData_order in Weigher4_1: no weigher data for a while and self.no_new_data_counter is %s'
                                             % self.no_new_data_counter)
                self.no_new_data_counter = 1
                self.no_new_data_error.emit()
            else:
                self.mylogger4_1weigher.debug('acceptData_order in Weigher4_1: self.no_new_data_counter is %s'
                                             % self.no_new_data_counter)

        else:
            self.no_new_data_counter = 0

            # step1: extracting data
            # At this time, the data ranging from current_data_start_index to current_data_end_index will be the data.
            data1 = self.serial_port_buffer[current_data_start_index: current_data_end_index]
            # self.mylogger4_1weigher.debug('acceptData_order: %s' % data1)
            try:
                # without the strip, error happens in float() operation, such as invisible character
                data2 = str(data1, encoding='utf-8').strip()
                if current_data_start_index < 0 or current_data_end_index < 0:
                    self.mylogger4_1weigher.debug('The length of data is %s and the value part is: %s' % (len(data2), data2))
                self.current_data = float(data2[1: -2]) * 1000
                # self.mylogger4_1weigher.debug('The editted part of data is: %s' % self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger4_1weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_order and force it to be the last data.'
                    , exc_info=True)

            # step2: processing data
            if self.current_data > 2:
                if self.last_data == self.current_data:
                    # if true, the weigher must send two successive same data.
                    # Since the value of the last data is the same as the current data, we do not need to refresh the self.last_data
                    if self.record_value + 2 < self.current_data or self.current_data < self.record_value - 2 or self.wave_status:
                        # print('Weigher says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.mylogger4_1weigher.info('Weigher4_1 says there is significant change from %s to %s.' % (self.record_value, self.current_data))
                        self.record_value = self.current_data
                        self.wave_status = False
                        self.serial_port_timer.timeout.disconnect(self.acceptData_order)
                        self.detect_changed.emit(self.current_data)
                    else:
                        # print('Weigher says that the record value is the same as the current data.')
                        # self.mylogger4_1weigher.debug('Weigher4_1 says that the record value is the same as the current data.')
                        pass
                else:
                    if self.last_data + 3 < self.current_data or self.current_data < self.last_data - 3:
                        self.wave_status = True
                    self.last_data = self.current_data  # refreshing the value of last data.
            else:
                # this situation says that self.current_data <= 2 (unit: g), which indicates there is nothing in the payment system.
                # if both current dat and last data are less than 2g, there is no need to refresh the value of the last data.
                if self.record_value > 2:
                    # print('Weigher detects significant change %s to zero.' % self.record_value)
                    self.mylogger4_1weigher.info('Weigher4_1 detects significant change %s to zero.' % self.record_value)
                    self.record_value = self.current_data
                    self.empty.emit()
                else:
                    # print('Weigher detects nothing with %s.' % self.current_data)
                    self.mylogger4_1weigher.debug('Weigher4_1 detects nothing with %s.' % self.current_data)

            # step3: cleaning buffer
            # If the latest part cannot be converted to float successfully and no data is sent anymore, this will result
            # in the bug of detecting error. Therefore, I clean the buffer every time.
            discard = self.serial_port_buffer.remove(0, current_data_end_index)  # does not delete the right boundary

    def acceptData_back_to_standby(self):
        """
        To accelerate the process which is back to the standby layout;
        This slot will be connected with the timeout signal of the QTimer object;
        The data part is extracted based on two different '\n'.
        """
        # you need to ensure there are different b'\n' in the buffer since the backward searching includes the start point
        current_data_end_index = self.serial_port_buffer.lastIndexOf(b'\n',-1)  # searching backward from the last one
        if current_data_end_index < 1:
            # current_data_end_index is equal to 0 or -1
            current_data_start_index = -1
        else:
            # Be careful that 'current_data_end_index=0' results in 'current_data_start_index=0'
            current_data_start_index = self.serial_port_buffer.lastIndexOf(b'\n', current_data_end_index - 1)
        # self.mylogger4_1weigher.debug('acceptData_back_to_standby: slicing [%s, %s]' % (current_data_start_index, current_data_end_index))

        if current_data_start_index == -1:
            # error detection
            self.no_new_data_counter = self.no_new_data_counter + 1
            if self.no_new_data_counter > self.no_new_data_boundary:
                self.mylogger4_1weigher.error(
                    'acceptData_back_to_standby in Weigher4_1: no weigher data for a while and self.no_new_data_counter is %s'
                                              % self.no_new_data_counter)
                self.no_new_data_counter = 1
                self.no_new_data_error.emit()
            else:
                self.mylogger4_1weigher.debug('acceptData_back_to_standby in Weigher4_1: self.no_new_data_counter is %s'
                                              % self.no_new_data_counter)
        else:
            self.no_new_data_counter = 0

            # step1: extracting data
            # At this time, the data ranging from current_data_start_index to current_data_end_index will be the data.
            data1 = self.serial_port_buffer[current_data_start_index: current_data_end_index]
            # self.mylogger4_1weigher.debug('acceptData_back_to_standby: %s' % data1)
            try:
                # without the strip, error happens in float() operation, such as invisible character
                data2 = str(data1, encoding='utf-8').strip()
                if current_data_start_index < 0 or current_data_end_index < 0:
                    self.mylogger4_1weigher.debug('The length of data is %s and the value part is: %s' % (len(data2), data2))
                self.current_data = float(data2[1: -2]) * 1000
                # self.mylogger4_1weigher.debug('The editted part of data is: %s' % self.current_data)
            except BaseException:
                self.current_data = self.last_data
                self.mylogger4_1weigher.error(
                    'Cannot convert the data given by the weigher in acceptData_back_to_standby and force it to be the last data.'
                    , exc_info=True)

            # step2: processing data
            if self.last_data + 2 < self.current_data or self.current_data < self.last_data - 2:
                self.serial_port_timer.timeout.disconnect(self.acceptData_back_to_standby)
                self.to_standby.emit()

            # step3: cleaning buffer
            # If the latest part cannot be converted to float successfully and no data is sent anymore, this will result
            # in the bug of detecting error. Therefore, I clean the buffer every time.
            discard = self.serial_port_buffer.remove(0, current_data_end_index)  # does not delete the right boundary

    def handling_serial_port_error(self, error_code):
        """
        This function is called after the QSerialPort.errorOccurred signal is emitted.
        :param error_code: <class 'PyQt5.QtSerialPort.QSerialPort.SerialPortError'>
        :return:
        """
        self.mylogger4_1weigher.info('%s: handling_serial_port_error starts' %self.__class__)
        error_code_str = str(error_code)
        if error_code_str == '8':
            # QSerialPort.ReadError will emit many many times if you unplug the serial port when reading
            pass
        elif error_code_str == '0':
            # using QSerialPort.close() will result in the execution of below codes.
            # self.mylogger4_1weigher.info('Weigher4_1 with %s: %s' % (error_code_str, self.serial_port_error_dict.get(error_code_str)))
            pass
        elif error_code_str in ['1','2','3','9','13']:
            self.mylogger4_1weigher.info('%s with %s: %s and try to reopen weigher later'
                                    % (self.__class__, error_code_str, self.serial_port_error_dict.get(error_code_str)))
            self.reopening_related_timer.start(self.reopening_timer_interval)
        else:
            self.mylogger4_1weigher.error('%s with %s: %s and no successive process'
                                    % (self.__class__, error_code_str, self.serial_port_error_dict.get(error_code_str)))
        self.mylogger4_1weigher.info('%s: handling_serial_port_error ends' %self.__class__)

    def trying2reopen_serial_port(self):
        """
          Be careful, the execution of QSerialPort.close() and QSerialPort.open() will result in the emission of
        errorOccurred signal and then the execution fo handling_serial_port_error function.
        :return: 
        """
        self.mylogger4_1weigher.info('%s: trying2reopen_serial_port starts' %self.__class__)
        if self.serial.isOpen():
            self.mylogger4_1weigher.info('%s: closing the weigher' %self.__class__)
            self.serial.close()  # will result will emit the errorOccurred signal with QSerialPort.NoError
            self.reopening_related_timer.start(self.reopening_timer_interval)
        elif self.serial.open(QIODevice.ReadOnly):
            self.mylogger4_1weigher.info('%s: the connection of the weigher is successful' %self.__class__)
        else:
            self.mylogger4_1weigher.info('%s: the connection of the weigher is failed.' %self.__class__)
        self.mylogger4_1weigher.info('%s: trying2reopen_serial_port ends' %self.__class__)


class MainWindow(QFrame):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.layout_init()
        self.layout_manage()
        #
        self.index = 0
        self.serial_port = Weigher4_1(port_name='COM3')
        
        #
        self.pre_work()
    
    
    def pre_work(self):
        self.serial_port.serial_port_timer.timeout.connect(self.timeout_record)
        self.serial_port.serial_port_timer.start()  # should be started after all initialization of threads

    def layout_init(self):
        self.setFixedSize(640, 480)
        self.button = QPushButton('close', self)
        self.button.setFixedSize(100, 100)
        self.button.clicked.connect(self.open_serial_port)

        self.button2 = QPushButton('open', self)
        self.button2.setFixedSize(100, 100)
        self.button2.clicked.connect(self.close_serial_port)

        self.button3 = QPushButton('test01', self)
        self.button3.setFixedSize(200, 100)
        self.button3.clicked.connect(self.test01)

    def layout_manage(self):
        self.button.move(0, 0)
        self.button2.move(100, 0)
        self.button3.move(0, 100)

    def open_serial_port(self):
        # The serial port has to be open before trying to close it; otherwise sets the NotOpenError error code
        self.serial_port.serial.close()
        print('disconnection to the serial port is successful.')

    def close_serial_port(self):
        if self.serial_port.serial.open(QIODevice.ReadOnly):
            print('reconnection to the serial port is successful.')
        else:
            print('reconnection to the serial port is failed.')
    
    def timeout_record(self):
        self.index = self.index + 1
        mylogging.logger.info(self.index)

    def test01(self):
        self.serial_port.serial_port_timer.timeout.connect(self.serial_port.acceptData_standby)


if __name__ == '__main__':
    mylogging = MyLogging1(logger_name='hobin')
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

