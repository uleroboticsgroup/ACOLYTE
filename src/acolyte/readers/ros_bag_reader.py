"""
This is a class-containing module.

It contains the RosBagReader class, which is responsible for reading the topic messages from the
specified rosbag file.
It also creates and stores the system data records that are generated.
"""


import hashlib
import logging
import time
import rosbag2_py
from multiprocessing import Process

from cv_bridge import CvBridge

from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

from bcubed.blockchain.node import Node
from bcubed.constants.records.fields.id_value_fields import IdValueFields
from bcubed.constants.records.fields.system_data_fields import SystemDataFields
from bcubed.constants.records.fields.meta_data_fields import MetaDataFields
from bcubed.records.fields.id_uint8_value_string_field import IdUint8ValueStringField
from bcubed.records.meta_data_record import MetaDataRecord

from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys
from acolyte.constants.rosbag_files import RosBagFileExtensions, RosBagFileTypes
from acolyte.readers.reader import Reader
from acolyte.readers.operating_system_static_reader import OperatingSystemStaticInfo
from acolyte.reader_daemons.operating_system_reader_daemon import OperatingSystemReaderDaemon


SERIALIZATION_FORMAT = "cdr"


class RosBagReader(Reader):
    """
    It reads topic messages from the specified rosbag file and creates and stores the records
    that are generated from these messages.
    """

    __logger = logging.getLogger(__name__)

    def __init__(self, node: Node, reader: rosbag2_py.SequentialReader, rosbag_file: str, operating_system: bool):
        self.__rosbag_file = rosbag_file
        self.__file_type = self.__get_file_type()
        self.__topics = AcolyteConfig().get_property(ConfigCategories.TOPICS)
        self.__operating_system = operating_system

        self.__reader = reader
        self.__configure_reader()
        self.__os_static_info = OperatingSystemStaticInfo()

        self.__ros_bag_messages = self.__reader.get_metadata().message_count
        self.__readed_messages = 0

        self.__ros_bag_reading_retry = AcolyteConfig().get_property(
            ConfigKeys.ROSBAG_READING_RETRY, ConfigCategories.TIMINGS)

        super().__init__(node)

    def __run_os_reader_daemon(self):
        os_reader_daemon = OperatingSystemReaderDaemon(self._node)
        os_reader_daemon.start()

    def __run_daemon(self, daemon_function):
        self.__logger.info("Running daemon...")

        daemon = Process(target=daemon_function, args=[], daemon=False)

        daemon.start()
        daemon.join()

    def __restart_reader(self):
        self.__reader = rosbag2_py.SequentialReader()
        self.__configure_reader()

    def __configure_reader(self):
        self.__reader.open(
            rosbag2_py.StorageOptions(
                uri=self.__rosbag_file, storage_id=self.__file_type),
            rosbag2_py.ConverterOptions(
                input_serialization_format=SERIALIZATION_FORMAT,
                output_serialization_format=SERIALIZATION_FORMAT,
            ),
        )

        storage_filter = rosbag2_py.StorageFilter(
            topics=list(self.__topics.keys()))
        self.__reader.set_filter(storage_filter)

    def __get_file_type(self):
        rosbag_file_splitted = self.__rosbag_file.split(".")
        extension = rosbag_file_splitted[len(rosbag_file_splitted) - 1]

        file_type = None

        if extension == RosBagFileExtensions.DB3:
            file_type = RosBagFileTypes.SQLITE

        elif extension == RosBagFileExtensions.MCAP:
            file_type = RosBagFileTypes.MCAP

        return file_type

    def __read_messages(self):
        topic_types = self.__reader.get_all_topics_and_types()
        type_map = {
            topic_types[i].name: topic_types[i].type for i in range(len(topic_types))
        }

        i = 0

        while self.__reader.has_next():
            topic, data, timestamp = self.__reader.read_next()

            msg_type = get_message(type_map[topic])
            msg = deserialize_message(data, msg_type)

            yield topic, msg, msg_type, timestamp, i

            i += 1

        self.__logger.info("%s messages have been processed.", i)

    def create_meta_data_record(self, name: str, responsible: str):
        meta_data_record = MetaDataRecord(responsible)

        meta_data_record[MetaDataFields.FIELD_SYS_N] = self.__os_static_info.get_system_name()
        meta_data_record[MetaDataFields.FIELD_SYS_V] = self.__os_static_info.get_release_version()
        meta_data_record[MetaDataFields.FIELD_SYS_S] = self.__os_static_info.get_serial_number()
        meta_data_record[MetaDataFields.FIELD_SYS_M] = self.__os_static_info.get_vendor_id(
        )
        meta_data_record[MetaDataFields.FIELD_BBN_V] = name
        meta_data_record[MetaDataFields.FIELD_NET_ID] = self.__os_static_info.get_network_name()
        meta_data_record[MetaDataFields.FIELD_OSY_T] = self.__os_static_info.get_operating_system_type(
        )
        meta_data_record[MetaDataFields.FIELD_SYS_P] = self.__os_static_info.get_system_processors(
        )

        return meta_data_record

    def get_messages(self):

        if self.__operating_system:
            self.__run_daemon(self.__run_os_reader_daemon)

        bridge = CvBridge()

        for topic, msg, msg_type, timestamp, i in self.__read_messages():
            # self.__logger.info("Topic: %s", topic)
            # self.__logger.info("Timestamp %s", timestamp)
            # self.__logger.info("Message type %s", msg_type)
            # self.__logger.info("Message %s", msg)
            # self.__logger.info("\n")

            if i < self.__readed_messages:
                continue

            if topic == "/joy_priority":
                self._create_and_store_system_data_record(
                    int(timestamp), SystemDataFields.FIELD_AUT_B, msg.data)

            elif topic == "/head_front_camera/rgb/image_raw":
                cv_image = bridge.imgmsg_to_cv2(
                    msg, desired_encoding="passthrough")
                image_hash = hashlib.sha256(cv_image).hexdigest()

                value = IdUint8ValueStringField(
                    {IdValueFields.FIELD_ID: self.__topics[topic], IdValueFields.FIELD_VALUE: str(image_hash)})

                self._create_and_store_system_data_record(
                    int(timestamp), SystemDataFields.FIELD_CAM_F, value)

            else:
                value = IdUint8ValueStringField(
                    {IdValueFields.FIELD_ID: self.__topics[topic], IdValueFields.FIELD_VALUE: str(msg)})

                self._create_and_store_system_data_record(
                    int(timestamp), SystemDataFields.FIELD_SYS_X, value
                )

            self.__readed_messages += 1

            if self.__readed_messages != 0 and self.__readed_messages % 200 == 0:
                self.__logger.info("Processed messages: %s",
                                   self.__readed_messages)

        self.__restart_reader()

        # This is necessary if the blockchain network is as fast as the Rosbag recording
        if self.__ros_bag_messages == self.__reader.get_metadata().message_count:
            time.sleep(self.__ros_bag_reading_retry)
            self.__restart_reader()

        if self.__ros_bag_messages != self.__reader.get_metadata().message_count:
            self.__ros_bag_messages = self.__reader.get_metadata().message_count
            self.__logger.info(
                "Let's try another read (%d messages)", self.__ros_bag_messages)
            self.get_messages()
