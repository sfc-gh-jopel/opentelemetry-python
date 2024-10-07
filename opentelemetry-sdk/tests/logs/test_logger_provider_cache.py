import logging
import unittest

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    InMemoryLogExporter,
    SimpleLogRecordProcessor,
)


def set_up_logging_handler(level):
    logger_provider = LoggerProvider()
    exporter = InMemoryLogExporter()
    processor = SimpleLogRecordProcessor(exporter=exporter)
    logger_provider.add_log_record_processor(processor)
    handler = LoggingHandler(level=level, logger_provider=logger_provider)
    return handler, logger_provider


def create_logger(handler, name):
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    return logger


class TestLoggerProviderCache(unittest.TestCase):

    def test_get_logger_single_handler(self):
        handler, logger_provider = set_up_logging_handler(level=logging.DEBUG)
        # pylint: disable=protected-access
        logger_cache = logger_provider._logger_cache
        logger = create_logger(handler, "test_logger")

        # Ensure logger is lazily cached
        self.assertEqual(0, len(logger_cache))

        logger.warning("test message")

        self.assertEqual(1, len(logger_cache))

        # Ensure only one logger is cached
        rounds = 100
        for _ in range(rounds):
            logger.warning("test message")

        self.assertEqual(1, len(logger_cache))

    def test_get_logger_multiple_loggers(self):
        handler, logger_provider = set_up_logging_handler(level=logging.DEBUG)
        # pylint: disable=protected-access
        logger_cache = logger_provider._logger_cache

        num_loggers = 10
        loggers = [create_logger(handler, str(i)) for i in range(num_loggers)]

        # Ensure loggers are lazily cached
        self.assertEqual(0, len(logger_cache))

        for logger in loggers:
            logger.warning("test message")

        self.assertEqual(num_loggers, len(logger_cache))

        rounds = 100
        for _ in range(rounds):
            for logger in loggers:
                logger.warning("test message")

        self.assertEqual(num_loggers, len(logger_cache))
