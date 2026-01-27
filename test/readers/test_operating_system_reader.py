"""
This is a class-containing module.

It contains the GivenAnOperatingSystemReader class, which inherits from TestCase and
performs all the OperatingSystemReader tests.
"""


from unittest import TestCase
from unittest.mock import MagicMock

import logging

from test.config.config_test_helper import ConfigTestHelper

from acolyte.readers.operating_system_reader import OperatingSystemReader


CLASS_PATH = 'acolyte.readers.operating_system_reader'


class GivenAnOperatingSystemReader (TestCase):
    """
    It contains the test suite related with OperatingSystemReader class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.config_test_helper = ConfigTestHelper()
        self.config_test_helper.create_test_config_file()

        self.node = MagicMock()
        self.node.store_system_data_record = MagicMock()

        self.os_operating_system_reader = OperatingSystemReader(self.node)

        return super().setUp()

    def tearDown(self):
        del self.os_operating_system_reader

        self.config_test_helper.tear_down()

        return super().tearDown()

    def test_when_getting_messages_then_store_system_data_record_is_called_four_times(self):
        self.os_operating_system_reader.get_messages()

        self.node.store_system_data_record.assert_called()

        self.assertEqual(
            len(self.node.store_system_data_record.call_args_list), 4)
