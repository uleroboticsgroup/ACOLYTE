"""
This is a class-containing module.

It contains the RosBagReader class, which is responsible for reading the topic messages from the
specified rosbag file.
It also creates and stores the system data records that are generated.
"""

import hashlib
import logging
import rosbag2_py

from cv_bridge import CvBridge

from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

from bcubed.blockchain.node import Node
from bcubed.constants.records.fields.id_value_fields import IdValueFields
from bcubed.constants.records.fields.system_data_fields import SystemDataFields
from bcubed.records.fields.id_uint8_value_string_field import IdUint8ValueStringField

from acolyte.config.config import Config
from acolyte.constants.config_keys import ConfigKeys
from acolyte.constants.rosbag_files import RosBagFileExtensions, RosBagFileTypes
from acolyte.readers.reader import Reader


SERIALIZATION_FORMAT = "cdr"


class RosBagReader(Reader):
    """
    It reads topic messages from the specified rosbag file and creates and stores the records
    that are generated from these messages.
    """

    __logger = logging.getLogger(__name__)

    def __init__(self, node: Node, rosbag_file: str):
        self.__rosbag_file = rosbag_file
        self.__file_type = self.__get_file_type()
        self.__topics = Config().get_property(ConfigKeys.TOPICS)
        self.__reader = self.__configure_reader()
        self.__ros_bag_messages = self.__reader.get_metadata().message_count
        self.__readed_messages = 0

        super().__init__(node)

    def __configure_reader(self):
        reader = rosbag2_py.SequentialReader()
        reader.open(
            rosbag2_py.StorageOptions(
                uri=self.__rosbag_file, storage_id=self.__file_type),
            rosbag2_py.ConverterOptions(
                input_serialization_format=SERIALIZATION_FORMAT,
                output_serialization_format=SERIALIZATION_FORMAT,
            ),
        )

        storage_filter = rosbag2_py.StorageFilter(
            topics=list(self.__topics.keys()))
        reader.set_filter(storage_filter)

        return reader

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

    def get_messages(self):
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

        self.__reader = self.__configure_reader()

        if self.__ros_bag_messages != self.__reader.get_metadata().message_count:
            self.__ros_bag_messages = self.__reader.get_metadata().message_count
            self.__logger.info(
                "Let's try another read (%d messages)", self.__ros_bag_messages)
            self.get_messages()
