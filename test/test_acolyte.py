"""
This is a class-containing module.

It contains the GivenAnAcolyte class, which inherits from TestCase and performs all the
Acolyte tests.
"""

import argparse
from unittest import TestCase
from unittest.mock import MagicMock

import logging

from acolyte.acolyte import Acolyte
from acolyte.constants.arguments import Arguments


CLASS_PATH = 'acolyte.acolyte'


class GivenAnAcolyte (TestCase):
    """
    It contains the test suite related with Acolyte class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.arguments = argparse.Namespace(action=Arguments.ACTION_GET_BY_TIMESTAMP,
                                            responsible='test', timestamp_start=0,
                                            timestamp_end=10)
        self.bcubed = MagicMock()

        self.acolyte = Acolyte(self.bcubed)

        return super().setUp()

    def test_when_getting_by_timestamp_and_bcubed_is_not_initialized_it_finishes_and_log_it(self):
        with self.assertLogs(self.__logger, level="ERROR") as log:
            self.acolyte.run(self.arguments)

            self.assertEqual(
                log.output[0], 'ERROR:' + CLASS_PATH +
                ':BCubed is not initialized with Meta Data Record.')
