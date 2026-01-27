"""
This is a class-containing module.

It contains the GivenARosBagReader class, which inherits from TestCase and
performs all the RosBagReader tests.
"""


from unittest import TestCase
from unittest.mock import MagicMock


from acolyte.readers.ros_bag_reader import RosBagReader


class GivenARosBagReader (TestCase):
    """
    It contains the test suite related with RosBagReader class.
    Add tests as required.
    """

    def setUp(self) -> None:
        self.node = MagicMock()
        self.node.store_system_data_record = MagicMock()

        self.reader = MagicMock()

        self.rosbag_file = "test/utilities/test.mcap"

        self.ros_bag_reader = RosBagReader(
            self.node, self.reader, self.rosbag_file, False)

        return super().setUp()

    def test_when_creating_a_ros_bag_reader_then_an_exception_rises(self):
        with self.assertRaises(ValueError) as context:
            self.ros_bag_reader.get_messages()

        self.assertEqual(
            context.exception.args[0], "not enough values to unpack (expected 3, got 0)")
