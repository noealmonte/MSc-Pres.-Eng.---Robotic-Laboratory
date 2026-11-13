'''
Copyright (C) BFH roboticsLab
All rights reserved.
'''

import logging
from enum import Enum, auto
from datetime import datetime


class Level(Enum):
  ''' Logging levels, copied from logging. '''
  DEBUG = logging.DEBUG
  INFO = logging.INFO
  WARNING = logging.WARNING
  ERROR = logging.ERROR
  CRITICAL = logging.CRITICAL
  SUCCESS = auto()
  DEPRECATED = auto()


'''
Logger class
@usageExample:
  import os
  from ch.bfh.roboticsLab.util.Logger import Logger
  logger = Logger(os.path.basename(__file__), level=Logger.Level.INFO, file='test')
  logger.warning('My warning message...')
'''


class Logger():
  fileHandlers = {}

  def __init__(self, name: str, level: Level = Level.DEBUG, file: str = None, appendDate: bool = False) -> None:
    '''
    Create a new Logger object

    :param str name: The name of this logger, will be displayed in every log message.
    :param Level level: The minimum level to log, defaults to Level.DEBUG.
    :param str file: Path to a file to write the log messages to, defaults to None.
    :param bool appendDate: If `True` appends the date and time of log creation to the file argument, defaults to `False`.
    '''
    # TODO: Consider adding an option to choose between a long or short log format

    self.logger = logging.getLogger(name)
    self.logger.setLevel(level.value)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level.value)
    ch.setFormatter(CustomFormatter())

    if file is not None:
      # Append date to file name if requested
      indexLastDot = file.rfind('.')
      if indexLastDot > 0 and indexLastDot < len(file) - 1:
        file = file[:indexLastDot]
      if indexLastDot == -1 and indexLastDot < len(file) - 1:
        if appendDate:
          file = file + '_' + datetime.now().strftime("%Y%m%d")
      file = file + '.log'
      # Create file handler which logs even debug messages
      if file not in Logger.fileHandlers:
        fh = logging.FileHandler(filename=file, mode='a')
        fh.setLevel(level.value)
        fh.setFormatter(FileFormatter())
        Logger.fileHandlers[file] = fh
      else:
        fh = Logger.fileHandlers[file]

    if not self.logger.handlers:
      self.logger.addHandler(ch)
      if file is not None:
        self.logger.addHandler(fh)

  def success(self, message: object) -> None:
    self.logger.error(message, extra={'type': Level.SUCCESS.name})

  def debug(self, message: object) -> None:
    self.logger.debug(message, extra={'type': Level.DEBUG.name})

  def info(self, message: object) -> None:
    self.logger.info(message, extra={'type': Level.INFO.name})

  def error(self, message: object) -> None:
    self.logger.error(message, extra={'type': Level.ERROR.name})

  def critical(self, message: object) -> None:
    self.logger.critical(message, extra={'type': Level.CRITICAL.name})

  def warning(self, message: object) -> None:
    self.logger.warning(message, extra={'type': Level.WARNING.name})

  def deprecated(self, message: object) -> None:
    self.logger.warning(message, extra={'type': Level.DEPRECATED.name})


class CustomFormatter(logging.Formatter):
  ''' https://github.com/mbadolato/iTerm2-Color-Schemes '''
  grey = "\x1b[38m"
  yellow = "\x1b[33m"
  blue = "\x1b[36m"
  green = "\x1b[32;1m"
  red = "\x1b[31m"
  magenta = "\x1b[35m"
  bold_red = "\x1b[31;1m"
  reset = "\x1b[0m"

  formatString = '%(asctime)-15s %(name)-8s [%(type)-8s] %(message)s'
  formatStringOld = '%(asctime)-15s %(name)-8s [%(levelname)-8s] %(message)s'
  FORMATS = {
      Level.DEBUG.name: grey + formatString + reset,
      Level.INFO.name: blue + formatString + reset,
      Level.WARNING.name: yellow + formatString + reset,
      Level.ERROR.name: red + formatString + reset,
      Level.CRITICAL.name: bold_red + formatString + reset,
      Level.SUCCESS.name: green + formatString + reset,
      Level.DEPRECATED.name: magenta + formatString + reset
  }

  def format(self, record):
    try:
      log_fmt = self.FORMATS.get(record.type)
    except:
      log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)


class FileFormatter(logging.Formatter):
  formatString = '%(asctime)-15s %(filename)-8s %(name)-8s [%(type)-8s] %(message)s'
  formatStringOld = '%(asctime)-15s %(name)-8s [%(levelname)-8s] %(message)s'
  FORMATS = {
      Level.DEBUG.name: formatString,
      Level.INFO.name: formatString,
      Level.WARNING.name: formatString,
      Level.ERROR.name: formatString,
      Level.CRITICAL.name: formatString,
      Level.SUCCESS.name: formatString,
  }

  def format(self, record):
    try:
      log_fmt = self.FORMATS.get(record.type)
    except:
      log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)


if __name__ == '__main__':
  import threading
  import time

  def test1():
    testLogger = Logger('myTestLogger', file='test', appendDate=True)
    testLogger.success('test success')
    testLogger.debug('test debug')
    testLogger.info('test info')
    testLogger.error('test error')
    testLogger.critical('test critical')
    testLogger.warning('test warning')
    time.sleep(0.1)
    testLogger.success('test')
    testLogger.success('test')
    testLogger.success('test')

  def test2():
    testLogger = Logger('myTestLogger2', file='test', appendDate=False)
    testLogger.success('test success')
    testLogger.debug('test debug')
    testLogger.info('test info')
    testLogger.error('test error')
    testLogger.critical('test critical')
    testLogger.warning('test warning')
    time.sleep(0.1)
    testLogger.success('test')
    testLogger.success('test')
    testLogger.success('test')

  # Test multithreading
  threading.Thread(target=test1).start()
  threading.Thread(target=test2).start()
