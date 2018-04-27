# -*- coding: utf-8 -*-
"""
In[1]: b'\x0d'.decode('ascii')
Out[1]: '\r'

Some non-printable bytes is represented from b'\x80' to b'\xFF'.
"""
import logging
import sys
from PyQt5.QtCore import QObject, QIODevice, Qt, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QApplication


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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout()
        self.button = QPushButton('disconnect')
        self.button.clicked.connect(self._mydisconnect)
        self.button2 = QPushButton('connect')
        self.button2.clicked.connect(self._myconnect)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.button2)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        #
        self.serial_port = Weigher1(port_name='COM3')


    def _mydisconnect(self):
        # The serial port has to be open before trying to close it; otherwise sets the NotOpenError error code
        self.serial_port.serial.close()
        print('disconnection to the serial port is successful.')


    def _myconnect(self):
        if self.serial_port.serial.open(QIODevice.ReadOnly):
            print('reconnection to the serial port is successful.')
        else:
            print('reconnection to the serial port is failed.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    sys.exit(app.exec_())

