# -*- coding: utf-8 -*-
"""

"""
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtSerialPort import QSerialPortInfo


def necessaryFind():
    """
    The main purpose of this function is to find all camera number, and the port name for weigher and door controller;
    :return:
    """
    # find the camera
    camera_device = QCamera()  # You have to declare QCamera object before using QCameraInfo.availableCameras()
    camera_list = QCameraInfo.availableCameras()
    for index, camera in enumerate(camera_list):
        print('-------------the current index is %s---------------' % index)
        print(camera.description())
        print(camera.deviceName())

    # find the weigher and the door controller
    serialPort_list = QSerialPortInfo.availablePorts()
    for index, serialPort in enumerate(serialPort_list):
        print('-------------the current index is %s---------------' % index)
        print(serialPort.description())
        print(serialPort.portName())
        print(serialPort.manufacturer())
        print(serialPort.systemLocation())
        print(serialPort.serialNumber())  # It returns the serial number string of the serial port, if available; otherwise returns an empty string.


if __name__ == '__main__':
    necessaryFind()

