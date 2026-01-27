"""
This is a class-containing module.

It contains the GivenAConfig class, which inherits from TestCase and performs all the
AcolyteConfig tests.
"""

from pathlib import Path
from unittest import TestCase

from test.config.config_test_helper import ConfigTestHelper
from test.config.constants import (
    CONF_FILE_NAME,
    VALUE_1,
    VALUE_2,
    VALUE_3,
    NON_EXISTENT
)

import logging
import os

from acolyte.config.acolyte_config import AcolyteConfig


CLASS_PATH = 'acolyte.config.acolyte_config'


class GivenAnAcolyteConfig (TestCase):
    """
    It contains the test suite related with AcolyteConfig class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.config_test_helper = ConfigTestHelper()
        self.config_test_helper.create_fake_config_file()

        self.config = AcolyteConfig()

        return super().setUp()

    def tearDown(self) -> None:
        del self.config

        self.config_test_helper.tear_down()

        return super().tearDown()

    def test_when_getting_another_config_instance_then_it_returns_the_same(self):
        other_config = AcolyteConfig()

        self.assertEqual(self.config, other_config)

    def test_when_getting_an_existent_property_then_it_returns_the_value(self):
        self.assertEqual(self.config.get_property(VALUE_1), {VALUE_2: VALUE_3})

    def test_when_getting_an_existent_property_with_category_then_it_returns_the_value(self):
        self.assertEqual(self.config.get_property(
            VALUE_2, VALUE_1), VALUE_3)

    def test_when_getting_a_non_existent_property_then_it_returns_none(self):
        self.assertEqual(self.config.get_property(NON_EXISTENT), None)

    def test_when_getting_a_non_existent_property_with_category_then_it_returns_none(self):
        self.assertEqual(self.config.get_property(
            NON_EXISTENT, VALUE_1), None)

    def test_when_getting_a_property_with_non_existent_category_then_it_returns_none(self):
        self.assertEqual(self.config.get_property(
            VALUE_2, NON_EXISTENT), None)

    def test_when_setting_a_property_then_it_stores_the_key_and_the_value(self):
        self.config.set_property(VALUE_1, {VALUE_3: VALUE_2})

        self.assertEqual(self.config.get_property(VALUE_1), {VALUE_3: VALUE_2})

    def test_when_setting_a_property_with_category_then_it_stores_the_key_and_the_value(self):
        self.config.set_property(VALUE_2, VALUE_2, VALUE_1)

        self.assertEqual(self.config.get_property(
            VALUE_2, VALUE_1), VALUE_2)

    def test_when_setting_a_property_and_config_file_not_exist_then_default_one_is_created_and_it_stores_the_key_and_the_value(self):
        conf_file = Path(CONF_FILE_NAME)
        if conf_file.exists():
            os.remove(CONF_FILE_NAME)

        self.config.set_property(VALUE_3, VALUE_3)
        self.assertEqual(self.config.get_property(VALUE_3), VALUE_3)

    def test_when_setting_a_property_and_the_config_file_has_bad_format_then_the_value_is_not_stored(self):
        with open(CONF_FILE_NAME, "a", encoding="utf-8") as file:
            file.write("h: t: c")

        self.config.set_property(VALUE_3, VALUE_2)

        self.assertNotEqual(VALUE_2, self.config.get_property(VALUE_3))

    def test_when_creating_config_without_config_file_then_it_logs_an_error_but_works(self):
        AcolyteConfig.clear()
        os.environ["ACOLYTE_CONF_FILE"] = "invalid"

        with self.assertLogs(self.__logger, level="ERROR") as log:
            self.config = AcolyteConfig()

            self.assertEqual(
                log.output[0], 'ERROR:' + CLASS_PATH + ':invalid file does not exist. A default empty one will be created.')

    def test_when_creating_config_with_bad_format_config_file_then_it_log_an_error_but_works(self):
        AcolyteConfig.clear()

        with open(CONF_FILE_NAME, "a", encoding="utf-8") as file:
            file.write("h: t: c")

        with self.assertLogs(self.__logger, level="ERROR") as log:
            self.config = AcolyteConfig()

            self.assertTrue(
                'ERROR:' + CLASS_PATH + ':mapping values are not allowed here' in log.output[0])
