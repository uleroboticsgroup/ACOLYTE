"""
This is a class-containing module.

It contains the Acolyte class, which is responsible for the ACOLYTE initialization.
"""

import logging
import sys
import rosbag2_py

from multiprocessing import Process
from bcubed.constants.records.fields.common_data_fields import CommonDataFields
from bcubed.records.overview_data_record import OverviewDataRecord

from acolyte.constants.arguments import Arguments
from acolyte.reader_daemons.operating_system_reader_daemon import OperatingSystemReaderDaemon
from acolyte.readers.rosbag_reader_creator import RosbagReaderCreator
from acolyte.readers.obd_reader_creator import OBDReaderCreator


class Acolyte:
    """
    It is responsible for the initialization of all the ACOLYTE dependencies and provides the
    instance to interact with.
    """

    __initial_account_balance = 0

    def __init__(self, bcubed):

        self.__black_box_name = bcubed.get_name()
        self.__node = bcubed.get_node()
        self.__logger = logging.getLogger(__name__)

    def __stop_os_reader_daemon(self):
        os_reader_daemon = OperatingSystemReaderDaemon(self.__node)
        os_reader_daemon.stop()

    def __stop_daemon(self, daemon_function):
        os_daemon = Process(target=daemon_function, args=[], daemon=False)

        os_daemon.start()
        os_daemon.join()

    def __get_records_by_timestamp(self, min_timestamp: int, max_timestamp: int):
        meta_data_record = self.__node.get_meta_data_record()

        if meta_data_record is not None and meta_data_record[CommonDataFields.FIELD_FIE_N] == 12:
            initial_timestamp = self.__node.get_initial_timestamp()
            final_timestamp = self.__node.get_final_timestamp()

            min_timestamp = min_timestamp if initial_timestamp < min_timestamp else initial_timestamp
            max_timestamp = max_timestamp if max_timestamp < final_timestamp else final_timestamp

            self.__logger.info(
                "Initial timestamp: %d - Final timestamp: %d", min_timestamp, max_timestamp)

            self.__node.get_system_data_records_by_timestamp(
                min_timestamp, max_timestamp)

            self.__node.get_overview_data_record()

            self.__logger.info(
                "Ether needed: %s", self.__initial_account_balance - self.__node.get_account_balance())

        else:
            self.__logger.error(
                "BCubed is not initialized with Meta Data Record.")

    def run(self, arguments):
        """
        Runs the application based on the arguments provided.
        """

        self.__initial_account_balance = self.__node.get_account_balance()
        self.__logger.info("Initial account balance: %s",
                           self.__initial_account_balance)

        if arguments.action == Arguments.ACTION_GET_BY_TIMESTAMP:
            self.__get_records_by_timestamp(
                int(arguments.timestamp_start), int(arguments.timestamp_end))

        elif arguments.action == Arguments.ACTION_STORE:
            if arguments.way == Arguments.WAY_ROSBAG:
                reader = rosbag2_py.SequentialReader()

                self.__messages_creator = RosbagReaderCreator(
                    self.__node, self.__black_box_name, reader, arguments)

            elif arguments.way == Arguments.WAY_OBD:
                self.__messages_creator = OBDReaderCreator(
                    self.__node, self.__black_box_name, arguments)

            else:
                self.__logger.error("Invalid way argument provided.")
                sys.exit()

            self.__messages_creator.read()

    def stop(self, arguments):
        """
        Stops the application and cleans the environment.
        """

        if arguments.action == Arguments.ACTION_STORE:
            if arguments.operating_system and arguments.way == Arguments.WAY_ROSBAG:
                self.__stop_daemon(self.__stop_os_reader_daemon)

            if arguments.way == Arguments.WAY_ROSBAG or arguments.way == Arguments.WAY_OBD:
                self.__logger.info(
                    "Storing remaining records and cleaning files...")

                self.__node.store_overview_data_record(OverviewDataRecord())

        self.__logger.info("Final account balance: %s",
                           self.__node.get_account_balance())
        self.__logger.info(
            "Ether needed: %s", self.__initial_account_balance - self.__node.get_account_balance())
