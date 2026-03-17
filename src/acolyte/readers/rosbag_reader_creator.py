"""
Concrete Creator for ROS Bag readers.
"""

from bcubed.blockchain.node import Node

from acolyte.readers.reader import Reader
from acolyte.readers.reader_creator import ReaderCreator
from acolyte.readers.ros_bag_reader import RosBagReader


class RosbagReaderCreator(ReaderCreator):
    """
    Concrete creator that creates RosBagReader instances.
    """

    def __init__(self, node: Node, name: str, reader, arguments):
        super().__init__(node, name, arguments)
        self._reader = reader
        self._rosbag_file = arguments.input_file
        self._operating_system = arguments.operating_system

    def factory_method(self) -> Reader:
        """
        Creates and returns a RosBagReader instance.
        """
        return RosBagReader(self._node, self._reader, self._rosbag_file, self._operating_system)
