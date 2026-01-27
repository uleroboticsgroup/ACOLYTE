"""
This is a class-containing module.

It contains the GivenAnOperatingSystemStaticInfo class, which inherits from TestCase and
performs all the OperatingSystemStaticInfo tests.
"""


from unittest import TestCase

import logging

from acolyte.readers.operating_system_static_reader import OperatingSystemStaticInfo


CLASS_PATH = 'acolyte.readers.operating_system_static_reader'


class GivenAnOperatingSystemStaticInfo (TestCase):
    """
    It contains the test suite related with OperatingSystemStaticInfo class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:

        self.os_operating_system_reader = OperatingSystemStaticInfo()

        return super().setUp()

    def tearDown(self):
        del self.os_operating_system_reader

        return super().tearDown()

    def test_when_getting_system_name_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_system_name(), "")

    def test_when_getting_release_version_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_release_version(), "")

    def test_when_getting_serial_number_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_serial_number(), "")

    def test_when_getting_vendor_id_then_it_returns_zeros(self):
        self.assertEqual(
            self.os_operating_system_reader.get_serial_number(), "0000000000000000")

    def test_when_getting_vendor_id_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_vendor_id(), "")

    def test_when_getting_network_name_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_network_name(), "")

    def test_when_getting_operating_system_type_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_operating_system_type(), "")

    def test_when_getting_system_procesors_then_it_returns_something(self):
        self.assertNotEqual(
            self.os_operating_system_reader.get_system_processors(), "")
