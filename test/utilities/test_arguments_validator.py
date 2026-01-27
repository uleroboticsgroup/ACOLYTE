"""
This is a class-containing module.

It contains the GivenAnArgumentsValidator class, which inherits from TestCase and performs all the
ArgumentsValidator tests.
"""

import argparse
from unittest import TestCase

import logging

from acolyte.constants.arguments import Arguments
from acolyte.utilities.arguments_validator import ArgumentsValidator


CLASS_PATH = 'acolyte.utilities.arguments_validator'


class GivenAnArgumentsValidator (TestCase):
    """
    It contains the test suite related with ArgumentsValidator class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.arguments = argparse.Namespace(action=Arguments.ACTION_STORE, input_file='test/utilities/test.mcap',
                                            responsible='test', way=Arguments.WAY_ROSBAG, operating_system=True, timestamp_start=0, timestamp_end=1751284548735)

        self.arguments_validator = ArgumentsValidator(self.arguments)

        return super().setUp()

    def test_when_validating_arguments_and_they_are_correct_it_returns_true(self):
        self.assertTrue(self.arguments_validator.validate_arguments())

    def test_when_validating_arguments_and_they_are_empty_it_returns_an_attribute_error(self):
        arguments = argparse.Namespace()

        with self.assertRaises(AttributeError) as context:
            self.arguments_validator = ArgumentsValidator(arguments)

            self.arguments_validator.validate_arguments()

        self.assertEqual(
            context.exception.args[0], "'Namespace' object has no attribute 'action'")

    def test_when_validating_arguments_and_input_file_is_not_valid_then_returns_false(self):
        arguments = argparse.Namespace(
            action='store', input_file='/path/invalid', responsible='test', way=Arguments.WAY_ROSBAG)

        self.arguments_validator = ArgumentsValidator(arguments)

        self.assertFalse(self.arguments_validator.validate_arguments())

    def test_when_validating_arguments_and_responsible_name_is_not_valid_then_returns_false(self):
        arguments = argparse.Namespace(
            action='store', input_file='test/utilities/test.mcap', responsible='', way=Arguments.WAY_ROSBAG)

        self.arguments_validator = ArgumentsValidator(arguments)

        self.assertFalse(self.arguments_validator.validate_arguments())

    def test_when_getting_arguments_then_they_are_returned(self):
        arguments = self.arguments_validator.get_arguments()

        self.assertEqual(arguments, self.arguments)
