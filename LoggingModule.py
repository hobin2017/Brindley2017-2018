# -*- coding: utf-8 -*-
"""
Part of this logging module comes from LiuXue and another part comes from the Internet.
author = hobin;
email = '627227669@qq.com';
"""
import os
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class MyLogging1(object):
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
                    'formatter': 'formatter1'
                },
            },
            'loggers': None
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

        # 4, the automatic rotation of logging file.
        dir_file = os.path.join(dir_path, '%s%s.log' % (logger_name, datetime.now().strftime('%dD-%Hh-%M')))  # the absolute path of the file.
        # the value of the parameter 'when' could be 'S, M, H, D, W0, W1, W2, W3, W4, W5, W6, midnight'
        file_auto = TimedRotatingFileHandler(dir_file, when='H', interval=6, backupCount=1)
        file_auto.suffix = '%Y%m%d-%Hh%Mm%Ss.log'
        file_auto.setFormatter(logging.Formatter('%(asctime)s -- %(message)s'))
        self.logger.addHandler(file_auto)

if __name__ == '__main__':
    mylogging = MyLogging1(logger_name='hobin')  # This is a customized class;
    mylogging.logger.debug('haha')

