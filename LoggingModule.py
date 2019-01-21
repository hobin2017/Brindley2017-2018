# -*- coding: utf-8 -*-
"""
Part of this logging module comes from LiuXue and another part comes from the Internet.
author = hobin;
email = '627227669@qq.com';
"""
import os
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from datetime import datetime

class MyLogging1(object):
    """
    The name of the log file changes automatically based on time.
    """
    def __init__(self, logger_name='hobin'):
        # 1, The configuration below has no file to output.
        self.LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'formatter1': {
                    'format': '%(asctime)s %(levelname)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',  # It takes effect
                    'class': 'logging.StreamHandler',
                    'formatter': 'formatter1'  # It takes effect
                },
            },
            'loggers': None
        }
        self.LOGGING_CONFIG['loggers'] = {logger_name:{'handlers':['console',],'level':'DEBUG', 'propagate':False}}
        # 2, to get the absolute path of the log file.
        dir_path = os.path.join(os.path.dirname(__file__), 'log')  # the file is stored under the 'log' folder.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 3, taking effects
        logging.config.dictConfig(self.LOGGING_CONFIG)  # this command can not be executed after the logging.getLogger function because there is no specific logger name.
        self.logger = logging.getLogger(logger_name)  # return a logger with the specified name, creating it if necessary. If no name is specified, return the root logger.
        # After configuring the logger, if you want to change the configuration again, just execute logging.config.dictConfig() again.

        # 4, the automatic rotation of logging file.
        dir_file = os.path.join(dir_path, '%s%s.log' % (logger_name, datetime.now().strftime('%dD-%Hh-%M')))  # the absolute path of the file.
        # the value of the parameter 'when' could be 'S, M, H, D, W0, W1, W2, W3, W4, W5, W6, midnight'
        file_auto = TimedRotatingFileHandler(dir_file, when='H', interval=6, backupCount=1)
        file_auto.suffix = '%Y%m%d-%Hh%Mm%Ss.log'
        file_auto.setFormatter(logging.Formatter('%(asctime)s -- %(message)s'))
        self.logger.addHandler(file_auto)


class MyLogging1_2(object):
    """
    Compared with MyLogging1 class, using two logging.handlers to record information of different levels.
    """
    def __init__(self, logger_name='hobin', logger_error_name='error_hobin'):
        # 1, The configuration below has no file for output.
        self.LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'formatter1': {
                    'format': '%(asctime)s %(levelname)s: %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',  # It takes effect
                    'class': 'logging.StreamHandler',
                    'formatter': 'formatter1'  # It takes effect
                },
            },
            'loggers': None
        }
        #
        self.LOGGING_CONFIG['loggers'] = {logger_name: {'handlers': ['console', ], 'level': 'DEBUG', 'propagate': False}}
        # 2, to get the absolute path of the log file.
        dir_path = os.path.join(os.path.dirname(__file__), 'log')  # the file is stored under the 'log' folder.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 3, taking effects
        logging.config.dictConfig(self.LOGGING_CONFIG)  # this command can not be executed after the logging.getLogger function because there is no specific logger name.
        self.logger = logging.getLogger(logger_name)  # return a logger with the specified name, creating it if necessary. If no name is specified, return the root logger.
        # After configuring the logger, if you want to change the configuration again, just execute logging.config.dictConfig() again.

        # 4, the automatic rotation of logging file.
        created_time = datetime.now().strftime('%dD-%Hh-%M')
        dir_file01 = os.path.join(dir_path, '%s%s.log' % (logger_name, created_time))  # the absolute path of the file.
        dir_file02 = os.path.join(dir_path, '%s%s.log' % (logger_error_name, created_time))

        # 4.1, TimedRotatingFileHandler
        # the value of the parameter 'when' could be 'S, M, H, D, W0, W1, W2, W3, W4, W5, W6, midnight'
        file_auto01 = TimedRotatingFileHandler(dir_file01, when='H', interval=6, backupCount=1)
        file_auto01.setLevel(logging.DEBUG)
        file_auto01.suffix = '%Y%m%d-%Hh%Mm%Ss.log'
        file_auto01.setFormatter(logging.Formatter('%(asctime)s -- %(message)s'))
        self.logger.addHandler(file_auto01)

        # 4.2, TimedRotatingFileHandler
        # It just records only the error information
        file_auto02 = TimedRotatingFileHandler(dir_file02, when='H', interval=24, backupCount=1)
        file_auto02.setLevel(logging.ERROR)  # recording ERROR information
        file_auto02.setFormatter(logging.Formatter('%(asctime)s -- %(message)s'))
        self.logger.addHandler(file_auto02)


if __name__ == '__main__':
    mylogging = MyLogging1_2(logger_name='hobin')  # This is a customized class;
    mylogging.logger.debug('haha')
    mylogging.logger.error('aaaa')

