"""
This is a class-containing module.

It contains the OperatingSystemReaderDaemon class, which is responsible for launching the
functionality of the OperatingSystemReader instance.
"""

import argparse
from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys
from acolyte.reader_daemons.reader_daemon import ReaderDaemon
from acolyte.readers.operating_system_reader_creator import OsReaderCreator


class OperatingSystemReaderDaemon (ReaderDaemon):
    """
    It contains the operating system reader daemon file paths and the management of the daemon.
    """

    def __init__(self, node):
        self._node = node

        self.__daemon_working_dir = AcolyteConfig().get_property(
            ConfigKeys.DAEMON_WORKING_DIR, ConfigCategories.PATHS)
        self.__daemon_pid_file = AcolyteConfig().get_property(
            ConfigKeys.DAEMON_PID_FILE, ConfigCategories.PATHS)

        super().__init__(self.__daemon_working_dir, self.__daemon_pid_file)

    def _run_thread(self):
        self._logger.info("Running daemon thread.")

        while self._thread_continue:
            OsReaderCreator(self._node, "", argparse.Namespace()
                            ).factory_method().get_messages()

        del self._node
