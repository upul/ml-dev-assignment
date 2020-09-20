import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from sentiment.util.config_reader import Config


class Logger(object):
    """Utility class can be used to log information

    This is a convenient wrapper for Python's logging object.
    Logger class provides common interfaces such as
    `info`, 'debug`, and etc. for logging information.
    Read `LOGGING` section of the `config.josn' for
    configuration options of the Logging class.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.logger = logging.getLogger(
                Config().LoggingConfig().read('FILE_NAME'))
            cls._instance.logger.setLevel(
                logging.INFO)  # TODO: (upul) configure log-level
            cls._instance.logger.addHandler(cls._instance._init_file_handler())
            cls._instance.logger.addHandler(
                cls._instance._init_streaming_handler())

        return cls._instance

    @staticmethod
    def _init_streaming_handler():
        """

        """
        streaming = StreamHandler()
        log_formatter = logging.Formatter(
            Config().LoggingConfig().read('FORMATTER'))
        streaming.setFormatter(log_formatter)
        return streaming

    @staticmethod
    def _init_file_handler():
        """

        """
        file_name = Config().LoggingConfig().read('FILE_NAME')
        formatter = Config().LoggingConfig().read('FORMATTER')
        max_size = Config().LoggingConfig().read('MAX_FILE_SIZE')
        backup_count = Config().LoggingConfig().read('BACKUP_COUNT')
        mode = Config().LoggingConfig().read('MODE')

        file_handler = RotatingFileHandler(
            file_name,
            mode=mode,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding=None,
            delay=0)
        file_formatter = logging.Formatter(formatter)
        file_handler.setFormatter(file_formatter)
        return file_handler

    def info(self, message, prepender=None):
        """ Info method of the logging class

        Use this method for logging INFO messages.

        Arguments:
            message: The message which is going to log.

        Returns:
            None
        """
        self._instance.logger.info(message)

    def debug(self, message, prepender=None):
        """Debug method of the logging class

        Use this method for logging DEBUG messages.

        Arguments:
            msg: The message which is going to log.

        Returns:
            None
        """
        self._instance.logger.debug(message)

    def error(self, message, prepender=None):
        """Error method of the logging class

        Use this method for logging ERROR messages.

        Arguments:
            msg: The message which is going to log.

        Returns:
            None
        """
        self._instance.logger.error(message)

    def critical(self, message, prepender=None):
        """critical method of the logging class

        Use this method for logging CRITICAL messages.

        Arguments:
            msg: The message which is going to log.

        Returns:
            None
        """
        self._instance.logger.critical(message)

    def exception(self, exception, prepender=None):
        """ exception method of the logging class

        Use this method for logging python exceptions.

        Arguments:
            exception: The exception which is going to log.

        Returns:
            None
        """
        self._instance.logger.exception(exception)
