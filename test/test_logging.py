# -*- coding: utf-8 -*-
"""
LogRecord attributes are listed below:
    %(asctime)s  --Human-readable time. By default this is of the form ‘2003-07-08 16:49:45,896'.
    %(created)f  --Time when the LogRecord was created.
    %(relativeCreated)d  --Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
    %(filename)s
    %(funcName)s
    %(levelname)s  --Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    %(levelno)s  --Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    %(lineno)d  --Source line number where the logging call was issued (if available).
    %(module)s  --Module (name portion of filename).
    %(message)s
    %(name)s  --Name of the logger used to log the call.
    %(pathname)s  --Full pathname of the source file where the logging call was issued (if available).
    %(process)d
    %(processName)s
    %(thread)d
    %(threadName)s
"""
import os
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import time

from PyQt5.QtCore import QThread

# 1, The first way to create the log
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
        'formatter1': {
            'format': '%(asctime)s %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': './log/test_log.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'hobin': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

def MyLogger(logger_name=None):
    """
    This function actually consists of  the logging.getLogger() function and other commands.
    :param logger_name: If no name is specified, return the root logger.
    :return: a logger with the specified name, creating it if necessary.
    """
    #1, to get the absolute path of the log file. For example, os.path.dirname(__file__) -->  D:/01PythonFile/basicTest
    file_name = datetime.now().strftime('%Y-%m-%d')  # the file is named by the time and the suffix is '.log'.
    dir_path = os.path.join(os.path.dirname(__file__), 'log')  # the file is stored under the 'log' folder.
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    dir_file = os.path.join(dir_path, file_name + '.log')  # the absolute path of the file.
    LOGGING_CONFIG['handlers']['file']['filename'] = dir_file

    #2, to make the changes take effects.
    logging.config.dictConfig(LOGGING_CONFIG)  # this command can be executed after the logging.getLogger function.
    logger = logging.getLogger(logger_name)
    return logger

# 2.1, The second way to create the log
class MyLogging(object):
    """
    The name of the log file changes automatically based on time.
    """
    def __init__(self, logger_name):
        # 1, The configuration below has no file to output.
        self.LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d: %(message)s'
                },
                'simple': {
                    'format': '%(levelname)s: %(message)s'
                },
                'formatter1': {
                    'format': '%(asctime)s %(levelname)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                },
            },
            'loggers': {
                'hobin': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                    'propagate': False,
                },
            },
        }
        # 2, to get the absolute path of the log file.
        dir_path = os.path.join(os.path.dirname(__file__), 'log')  # the file is stored under the 'log' folder.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 3, taking effects
        logging.config.dictConfig(self.LOGGING_CONFIG)  # this command can not be executed after the logging.getLogger function because there is no specific logger name.
        self.logger = logging.getLogger(logger_name)  # return a logger with the specified name, creating it if necessary. If no name is specified, return the root logger.
        # After configuring the logger, if you want to change the configuration again, just execute logging.config.dictConfig() again.


        # 3, the automatic rotation of logging file.
        dir_file2 = os.path.join(dir_path, 'Brindley.topmost.log')  # the absolute path of the file.
        # when = 'S, M, H, D, W0, W1, W2, W3, W4, W5, W6, midnight'
        file_auto = TimedRotatingFileHandler(dir_file2, when='midnight', interval=1, backupCount=1)
        file_auto.suffix = '%Y%m%d-%Hh%Mm%Ss.log'
        self.logger.addHandler(file_auto)

# 2.2
class MyLogging1(object):
    """
    The name of the log file changes automatically based on time.
    Compared with the Mylogging class, this class
    """
    def __init__(self, logger_name):
        # 1, The configuration below has no file to output.
        self.LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d: %(message)s'
                },
                'simple': {
                    'format': '%(levelname)s: %(message)s'
                },
                'formatter1': {
                    'format': '%(asctime)s %(levelname)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                },
            },
            'loggers': {}
        }
        self.LOGGING_CONFIG['loggers'] = {logger_name:{'handlers':['console',],'level':'DEBUG', 'propagrate':False}}
        # 2, to get the absolute path of the log file.
        dir_path = os.path.join(os.path.dirname(__file__), 'log')  # the file is stored under the 'log' folder.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 3, taking effects
        logging.config.dictConfig(self.LOGGING_CONFIG)  # this command can not be executed after the logging.getLogger function because there is no specific logger name.
        self.logger = logging.getLogger(logger_name)  # return a logger with the specified name, creating it if necessary. If no name is specified, return the root logger.
        # After configuring the logger, if you want to change the configuration again, just execute logging.config.dictConfig() again.

        # 3, the automatic rotation of logging file.
        dir_file2 = os.path.join(dir_path, 'Brindley.log')  # the absolute path of the file.
        # the value of the parameter when could be 'S, M, H, D, W0, W1, W2, W3, W4, W5, W6, midnight'
        file_auto = TimedRotatingFileHandler(dir_file2, when='midnight', interval=1, backupCount=1)
        file_auto.suffix = '%Y%m%d-%Hh%Mm%Ss.log'
        file_auto.setFormatter(logging.Formatter('--%(asctime)s %(filename)s line%(lineno)d-- %(message)s'))
        self.logger.addHandler(file_auto)

# to do the simulation of the actual case
class MyThread(QThread):
    def __init__(self, num=1, logger_name = None):
        super(MyThread, self).__init__()
        self.num = num
        self._logger = logging.getLogger(logger_name)


    def run(self):
        status = True
        times = 3
        while status:
            self._logger.debug('There is a message from thread%s' %self.num)
            time.sleep(1)
            times = times - 1
            if times == 0:
                status = False


if __name__ == '__main__':
    # mylogger = MyLogger(logger_name='hobin')  # This is a function;
    a = MyThread(logger_name='hobin')
    b = MyThread(num=2, logger_name='hobin')
    a.start()
    b.start()
    # time.sleep(1)  # to check whether it might miss some information since the 'hobin' logger does not exist.
    mylogging = MyLogging1(logger_name='hobin')  # This is a customized class;
    while True:
        # mylogger.info('Hello World!')  # the string represents the message part in the formatter.
        mylogging.logger.info('Hello World!')
        time.sleep(8)

