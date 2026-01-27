"""
This is a class-containing module.

It contains the GivenAReaderDaemon class, which inherits from TestCase and
performs all the ReaderDaemon tests.
"""


import os
from pathlib import Path
import shutil
from unittest import TestCase

import logging

from test.config.config_test_helper import ConfigTestHelper

from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys
from acolyte.reader_daemons.reader_daemon import ReaderDaemon


CLASS_PATH = 'acolyte.reader_daemons.reader_daemon'


class GivenAReaderDaemon (TestCase):
    """
    It contains the test suite related with ReaderDaemon class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.config_test_helper = ConfigTestHelper()
        self.config_test_helper.create_test_config_file()

        self.daemon_working_dir = AcolyteConfig().get_property(
            ConfigKeys.DAEMON_WORKING_DIR, ConfigCategories.PATHS)
        self.daemon_pid_file = AcolyteConfig().get_property(
            ConfigKeys.DAEMON_PID_FILE, ConfigCategories.PATHS)

        self.os_reader_daemon = ReaderDaemon(
            self.daemon_working_dir, self.daemon_pid_file)

        return super().setUp()

    def tearDown(self) -> None:
        shutil.rmtree(self.daemon_working_dir, ignore_errors=True)

        return super().tearDown()

    def __create_tmp_files(self):
        with open(self.daemon_pid_file, "w", encoding="utf-8") as file:
            file.write("")

    def test_when_running_thread_then_it_logs_an_info(self):
        with self.assertLogs(self.__logger, level="INFO") as log:
            self.os_reader_daemon._run_thread()

        self.assertTrue('INFO:' + CLASS_PATH +
                        ':Running daemon thread.', log.output[0])

    def test_when_starting_and_temporary_folder_already_exists_then_it_logs_an_info(self):
        self.__create_tmp_files()

        with self.assertLogs(self.__logger, level="INFO") as log:
            self.os_reader_daemon.start()

        self.assertTrue('INFO:' + CLASS_PATH +
                        ':Daemon already running' in log.output[1])

    def test_when_stopping_thread_then_it_logs_an_info(self):
        with self.assertLogs(self.__logger, level="INFO") as log:
            self.os_reader_daemon._stop_thread()

        self.assertTrue('INFO:' + CLASS_PATH +
                        ':Stopping daemon thread.', log.output[0])

    def test_when_stopping_and_temporary_pid_file_exists_then_it_tries_to_kill_the_process(self):
        self.__create_tmp_files()

        with self.assertLogs(self.__logger, level="INFO") as log:
            self.os_reader_daemon.stop()

            self.assertTrue('INFO:' + CLASS_PATH +
                            ':Stopping daemon' in log.output[0])

            self.assertTrue('ERROR:' + CLASS_PATH +
                            ':ERROR' in log.output[1])

    def test_when_stopping_and_temporary_pid_file_does_not_exist_then_it_logs_an_error(self):
        with self.assertLogs(self.__logger, level="ERROR") as log:
            self.os_reader_daemon.stop()

            self.assertTrue('ERROR:' + CLASS_PATH +
                            ":Daemon is not running " in log.output[0])

    def test_when_deleting_reader_daemon_then_it_removes_all_files(self):
        del self.os_reader_daemon

        self.assertFalse(os.path.exists(Path(self.daemon_working_dir)))
        self.assertFalse(os.path.exists(Path(self.daemon_pid_file)))
