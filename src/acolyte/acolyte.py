"""
This is a class-containing module.

It contains the Acolyte class, which is responsible for the ACOLYTE initialization.
"""

import logging

from multiprocessing import Process
from time import sleep

from bcubed.bcubed import BCubed
from bcubed.constants.records.fields.common_data_fields import CommonDataFields
from bcubed.constants.records.fields.meta_data_fields import MetaDataFields
from bcubed.records.meta_data_record import MetaDataRecord
from bcubed.records.overview_data_record import OverviewDataRecord

from acolyte.constants.arguments import Arguments
from acolyte.reader_daemons.operating_system_reader_daemon import OperatingSystemReaderDaemon
from acolyte.readers.operating_system_reader import OperatingSystemReader
from acolyte.readers.ros_bag_reader import RosBagReader


class Acolyte:
    """
    It is responsible for the initialization of all the ACOLYTE dependencies and provides the
    instance to interact with.
    """

    __initial_account_balance = 0

    def __init__(self, arguments):
        self.__responsible = arguments.responsible

        bcubed = BCubed()
        self.__black_box_name = bcubed.get_name()
        self.__node = bcubed.get_node()
        self.__logger = logging.getLogger(__name__)

        if arguments.action == Arguments.ACTION_STORE:
            self.__create_readers(arguments)

    def __run_os_reader_daemon(self):
        os_reader_daemon = OperatingSystemReaderDaemon(self.__os_worker)
        os_reader_daemon.start()

    def __run_daemon(self, daemon_function):
        self.__logger.info("Running daemon...")

        daemon = Process(target=daemon_function, args=[], daemon=False)

        daemon.start()
        daemon.join()

    def __stop_os_reader_daemon(self):
        os_reader_daemon = OperatingSystemReaderDaemon(self.__os_worker)
        os_reader_daemon.stop()

    def __stop_daemon(self, daemon_function):
        os_daemon = Process(target=daemon_function, args=[], daemon=False)

        os_daemon.start()
        os_daemon.join()

    def __create_readers(self, arguments):
        self.__os_worker = OperatingSystemReader(self.__node)

        if arguments.way == Arguments.WAY_ROSBAG:
            self.__messages_worker = RosBagReader(
                self.__node, arguments.input_file)

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
                "Bcubed is not initialized with Meta Data Record.")

    def __create_meta_data_record(self, os_worker: OperatingSystemReader, name: str, responsible: str):
        meta_data_record = MetaDataRecord(responsible)

        meta_data_record[MetaDataFields.FIELD_SYS_N] = os_worker.get_system_name()
        meta_data_record[MetaDataFields.FIELD_SYS_V] = os_worker.get_release_version()
        meta_data_record[MetaDataFields.FIELD_SYS_S] = os_worker.get_serial_number()
        meta_data_record[MetaDataFields.FIELD_SYS_M] = os_worker.get_vendor_id()
        meta_data_record[MetaDataFields.FIELD_BBN_V] = name
        meta_data_record[MetaDataFields.FIELD_NET_N] = os_worker.get_network_name()
        meta_data_record[MetaDataFields.FIELD_OSY_T] = os_worker.get_operating_system_type(
        )
        meta_data_record[MetaDataFields.FIELD_SYS_P] = os_worker.get_system_processors(
        )

        return meta_data_record

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
            meta_data_record = self.__create_meta_data_record(
                self.__os_worker,
                self.__black_box_name,
                self.__responsible)

            self.__node.store_meta_data_record(meta_data_record)

            if arguments.operating_system:
                self.__run_daemon(self.__run_os_reader_daemon)

            if arguments.way == Arguments.WAY_ROSBAG:
                self.__messages_worker.get_messages()

    def stop(self, arguments):
        """
        Stops the application and cleans the environment.
        """

        if arguments.action == Arguments.ACTION_STORE:
            if arguments.operating_system:
                self.__stop_daemon(self.__stop_os_reader_daemon)

            self.__logger.info(
                "Storing remaining records and cleaning files...")

            sleep(10)

            self.__node.store_overview_data_record(OverviewDataRecord())

        self.__logger.info("Final account balance: %s",
                           self.__node.get_account_balance())
        self.__logger.info(
            "Ether needed: %s", self.__initial_account_balance - self.__node.get_account_balance())
