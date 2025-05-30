"""
This is a class-containing module.

It contains the OperatingSystemReaderDaemon class, which is responsible for launching the 
functionality of the OperatingSystemReader instance.
"""

from acolyte.reader_daemons.reader_daemon import ReaderDaemon
from acolyte.readers.operating_system_reader import OperatingSystemReader


DAEMON_WORKING_DIR = "/tmp/os_daemon/"
DAEMON_PID_FILE_PATH = "/tmp/os_daemon/os_daemon.pid"
DAEMON_TXT_FILE_PATH = "/tmp/os_daemon/os_daemon.txt"


class OperatingSystemReaderDaemon (ReaderDaemon):
    """
    It contains the operating system reader daemon file paths and the management of the daemon.
    """

    def __init__(self, os_reader: OperatingSystemReader):
        self.__os_reader = os_reader

        super().__init__(DAEMON_WORKING_DIR, DAEMON_PID_FILE_PATH, DAEMON_TXT_FILE_PATH)

    def _run_thread(self):
        self._logger.info("Running daemon thread.")

        while self._thread_continue:
            self.__os_reader.get_messages()

        del self._node
