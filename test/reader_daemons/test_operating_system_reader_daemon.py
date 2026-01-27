"""
This is a class-containing module.

It contains the GivenAnOperatingSystemReaderDaemon class, which inherits from TestCase and
performs all the OperatingSystemReaderDaemon tests.
"""


import shutil
from unittest import TestCase
from unittest.mock import MagicMock

import logging

from test.config.config_test_helper import ConfigTestHelper

from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys

from acolyte.readers.operating_system_reader import OperatingSystemReader
from acolyte.reader_daemons.operating_system_reader_daemon import OperatingSystemReaderDaemon


CLASS_PATH = 'acolyte.reader_daemons.reader_daemon'


class GivenAnOperatingSystemReaderDaemon (TestCase):
    """
    It contains the test suite related with OperatingSystemReaderDaemon class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.config_test_helper = ConfigTestHelper()
        self.config_test_helper.create_test_config_file()

        self.working_dir = AcolyteConfig().get_property(
            ConfigKeys.DAEMON_WORKING_DIR, ConfigCategories.PATHS)

        self.os_worker = OperatingSystemReader(MagicMock())
        self.os_worker.get_messages = MagicMock()

        self.os_reader_daemon = OperatingSystemReaderDaemon(self.os_worker)

        return super().setUp()

    def tearDown(self) -> None:
        shutil.rmtree(self.working_dir, ignore_errors=True)

        return super().tearDown()

    def test_when_running_thread_and_thread_continue_is_false_then_it_logs_an_info_and_stops(self):
        self.os_reader_daemon._thread_continue = False

        with self.assertLogs(self.__logger, level="INFO") as log:
            self.os_reader_daemon._run_thread()

            self.os_worker.get_messages.assert_not_called()

        self.assertTrue('INFO:' + CLASS_PATH +
                        ':Running daemon thread' in log.output[0])
