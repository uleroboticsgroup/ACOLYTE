"""
This is a class-containing module.

It contains the GivenAnObdReader class, which inherits from TestCase and
performs all the OBDReader tests.
"""


import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from acolyte.readers.obd_reader import OBDReader
from test.config.config_test_helper import ConfigTestHelper

CLASS_PATH = 'acolyte.readers.obd_reader'


class GivenAnObdReader (TestCase):
    """
    It contains the test suite related with OBDReader class.
    Add tests as required.
    """

    __logger = logging.getLogger(CLASS_PATH)

    def setUp(self) -> None:
        self.node = MagicMock()

        self.config_test_helper = ConfigTestHelper()
        self.config_test_helper.create_test_config_file()

        self.mock_conn = MagicMock()

        self.mock_response_success = MagicMock()
        self.mock_response_success.is_null.return_value = False
        self.mock_response_success.value = MagicMock(magnitude=2500.0)

        self.mock_response_null = MagicMock()
        self.mock_response_null.is_null.return_value = True

        self.obd_reader = OBDReader(self.node)

        return super().setUp()

    def tearDown(self) -> None:
        self.config_test_helper.tear_down()
        return super().tearDown()

    def test_when_getting_vehicle_identification_then_returns_defaults_values(self):
        """
        Tests that when OBD is not connected, get_vehicle_identification returns
        default simulated values for VIN and calibration ID.
        """

        with self.assertLogs(self.__logger, level="WARN") as log:
            vin, calibration_id = self.obd_reader.get_vehicle_identification()

        self.assertTrue('WARNING:' + CLASS_PATH +
                        ':OBD not connected. Using default values.' in log.output[0])
        self.assertEqual(vin, 'SIMULATED_VIN_123456')
        self.assertEqual(calibration_id, 'Generic OBD Simulator')

    def test_when_getting_messages_and_obd_does_not_connect_then_it_logs_an_info_and_a_warn(self):
        """
        Tests that when OBD connection fails, get_messages logs appropriate
        warning and info messages.
        """

        with self.assertLogs(self.__logger, level="INFO") as log:
            self.obd_reader.get_messages()

        expected_message = ('WARNING:' + CLASS_PATH +
                            ':Not connected to OBD-II on /dev/ttyUSB0')
        self.assertTrue(expected_message in log.output[0])

        self.assertTrue('INFO:' + CLASS_PATH +
                        ':OBD connection closed successfully.' in log.output[1])

    @patch('acolyte.readers.obd_reader.time.sleep')
    @patch('acolyte.readers.obd_reader.obd.OBD')
    def test_when_getting_messages_and_obd_connects_succesfully_then_it_logs_an_info_and_closes_connection(self, mock_obd_class, mock_sleep):
        """
        Tests that when OBD connects successfully, get_messages executes queries,
        handles keyboard interrupt gracefully, and closes the connection properly.
        """

        self.mock_conn.is_connected.return_value = True
        mock_obd_class.return_value = self.mock_conn

        self.mock_conn.query.return_value = self.mock_response_success

        mock_sleep.side_effect = KeyboardInterrupt()

        with self.assertLogs(self.__logger, level="INFO") as log:
            self.obd_reader.get_messages()

        self.assertTrue(
            any('Keyboard interrupt received' in msg for msg in log.output))
        self.mock_conn.close.assert_called_once()

        self.assertEqual(self.mock_conn.query.call_count, 31)
        self.assertEqual(self.node.store_system_data_record.call_count, 31)

    @patch('acolyte.readers.obd_reader.time.sleep')
    @patch('acolyte.readers.obd_reader.obd.OBD')
    def test_when_getting_messages_and_some_pids_fail_then_continues_with_others(self, mock_obd_class, mock_sleep):
        """
        Tests that when 3 specific PIDs return null responses, get_messages continues
        querying all 31 PIDs, stores only the 28 successful responses, and logs
        the summary with correct successful and failed query counts.
        """

        self.mock_conn.is_connected.return_value = True
        mock_obd_class.return_value = self.mock_conn

        failed_positions = {5, 15, 25}
        self.mock_conn.query.side_effect = [
            self.mock_response_null if i in failed_positions else self.mock_response_success
            for i in range(31)
        ]

        mock_sleep.side_effect = KeyboardInterrupt()

        with self.assertLogs(self.__logger, level="INFO") as log:
            self.obd_reader.get_messages()

        self.assertEqual(self.mock_conn.query.call_count, 31)

        self.assertEqual(self.node.store_system_data_record.call_count, 28)

        self.assertTrue(
            any('28 successful' in msg and '3 failed' in msg for msg in log.output))
