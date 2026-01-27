"""
This is a class-containing module.

It contains the ReaderDaemon class, which serves as the base class for all ReaderDaemons and
encompasses their shared functions.
"""

import logging
import os
import signal
import sys
import time

from abc import abstractmethod
from pathlib import Path

import daemon
import daemon.pidfile

from bcubed.bcubed import BCubed


ENCODING = "utf-8"
READ_MODE = "r"
APPENDING_MODE = "a"


class ReaderDaemon:
    """
    It contains the base class for all the ReaderDaemons.
    """

    def __init__(self, working_dir: str, pid_path: str):
        self._node = None

        self.__working_dir = working_dir
        self.__pid_path = pid_path

        self._thread_continue = True

        self._logger = logging.getLogger(__name__)

        if not os.path.exists(Path(self.__working_dir)):
            self._logger.info("Creating all files.")
            os.mkdir(Path(self.__working_dir))

    def __del__(self):
        max_time = 6

        while (os.path.exists(Path(self.__pid_path)) and max_time > 0):
            self._logger.info("Waiting for the daemon to stop.")
            time.sleep(3)
            max_time = max_time - 1

        for root, dirs, files in os.walk(self.__working_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        if os.path.exists(Path(self.__working_dir)):
            self._logger.info("Deleting all files.")
            os.rmdir(Path(self.__working_dir))

    @abstractmethod
    def _run_thread(self):
        self._logger.info("Running daemon thread.")

    def _stop_thread(self, signum=None, frame=None):
        self._logger.info("Stopping daemon thread.")
        self._thread_continue = False

    def start(self):
        """
        Starts the operating system reader daemon.
        """

        self._logger.info("Starting daemon.")

        if os.path.exists(Path(self.__pid_path)):
            self._logger.info(
                "Daemon already running (%s, %s exists).", self, self.__pid_path)

        else:
            with daemon.DaemonContext(
                stdout=sys.stdout,
                stderr=sys.stderr,
                signal_map={
                    signal.SIGTERM: self._stop_thread,
                    signal.SIGTSTP: self._stop_thread,
                    signal.SIGINT: self._stop_thread,
                    # signal.SIGKILL: self.thread_stop,  # SIGKILL is an Invalid argument
                    # signal.SIGUSR1: daemon_status,
                    # signal.SIGUSR2: daemon_status,
                },
                pidfile=daemon.pidfile.PIDLockFile(self.__pid_path),
                working_directory=self.__working_dir,
                detach_process=True,
                files_preserve=[
                    logging.root.handlers[0].stream.fileno(),
                    logging.root.handlers[1].stream.fileno(),
                ],
            ):
                bcubed = BCubed()

                self._node = bcubed.get_node()

                self._logger = logging.getLogger(__name__)
                self._logger.info("Running reader daemon.")

                self._run_thread()

    def stop(self):
        """
        Stops the reader daemon.
        """

        self._logger.info("Stopping daemon.")

        if os.path.exists(self.__pid_path):
            with open(self.__pid_path, READ_MODE, encoding=ENCODING) as file:
                try:
                    os.kill(int(file.readline()), signal.SIGTERM)

                except (ProcessLookupError, ValueError) as error:
                    os.remove(self.__pid_path)
                    self._logger.error("ERROR: %s", error)

        else:
            self._logger.error(
                "Daemon is not running (%s, %s does not exist).", self, self.__pid_path)
