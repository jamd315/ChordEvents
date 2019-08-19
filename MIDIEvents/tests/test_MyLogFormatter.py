import logging
from unittest import TestCase

logger = logging.getLogger("MIDIEvents")


class TestMyLogFormatter(TestCase):
    def test_debug(self):
        with self.assertLogs(logger, logging.DEBUG) as log_helper:
            msg = "this is a test at the DEBUG level"
            logger.debug(msg)
            self.assertEqual(log_helper.records[0].getMessage(), msg)

    def test_info(self):
        with self.assertLogs(logger, logging.INFO) as log_helper:
            msg = "this is a test at the INFO level"
            logger.info(msg)
            self.assertEqual(log_helper.records[0].getMessage(), msg)

    def test_warning(self):
        with self.assertLogs(logger, logging.WARNING) as log_helper:
            msg = "this is a test at the WARNING level"
            logger.warning(msg)
            self.assertEqual(log_helper.records[0].getMessage(), msg)

    def test_error(self):
        with self.assertLogs(logger, logging.ERROR) as log_helper:
            msg = "this is a test at the ERROR level"
            logger.error(msg)
            self.assertEqual(log_helper.records[0].getMessage(), msg)

    def test_critical(self):
        with self.assertLogs(logger, logging.CRITICAL) as log_helper:
            msg = "this is a test at the CRITICAL level"
            logger.critical(msg)
            self.assertEqual(log_helper.records[0].getMessage(), msg)
