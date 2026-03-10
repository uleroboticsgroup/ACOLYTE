"""
This is a class-containing module.

It contains the GivenAnExcelObdReader class, which inherits from TestCase and
performs all the ExcelOBDReader tests.
"""

import os
import pandas as pd
from unittest import TestCase
from unittest.mock import MagicMock
import tempfile

from acolyte.readers.excel_obd_reader import ExcelOBDReader
from bcubed.constants.records.fields.meta_data_fields import MetaDataFields
from test.config.config_test_helper import ConfigTestHelper


class GivenAnExcelObdReader(TestCase):
    """
    It contains the test suite related with ExcelOBDReader class.
    Add tests as required.
    """

    def setUp(self) -> None:
        self.node = MagicMock()

        self.config_test_helper = ConfigTestHelper()
        self.config_test_helper.create_test_config_file()

        # Simulate real OBD data in CSV
        obd_test_data = pd.DataFrame([
            {
                "TIMESTAMP": 1500385813440,
                "MODEL": "TestModel",
                "VEHICLE_ID": "V123",
                "MARK": "TestMark",
                "ENGINE_COOLANT_TEMP": "83",
                "ENGINE_LOAD": "35.7",
                "ENGINE_RPM": "741.0",
                "AIR_INTAKE_TEMP": "52",
                "SPEED": "0.0",
                "THROTTLE_POS": "12.0",
                "TIMING_ADVANCE": "29.8"
            }
        ])
        self.tempfile = tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv")
        self.input_file = self.tempfile.name
        obd_test_data.to_csv(self.input_file, index=False)
        self.tempfile.close()

        self.reader = ExcelOBDReader(self.node, self.input_file)

        return super().setUp()

    def tearDown(self) -> None:
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        self.config_test_helper.tear_down()
        return super().tearDown()

    def test_when_cleaning_value_then_number_is_handled(self):
        """Tests that clean_value correctly parses a string number with spaces."""
        self.assertEqual(self.reader.clean_value(" 123 "), 123.0)

    def test_when_cleaning_value_then_percentage_is_handled(self):
        """Tests that clean_value correctly parses a percentage string."""
        self.assertEqual(self.reader.clean_value("21%"), 21.0)

    def test_when_cleaning_value_then_invalid_string_is_handled(self):
        """Tests that clean_value returns the original string if it cannot be parsed as a number."""
        self.assertEqual(self.reader.clean_value(
            "not_a_number"), "not_a_number")

    def test_when_cleaning_value_then_integer_is_handled(self):
        """Tests that clean_value returns an integer as is."""
        self.assertEqual(self.reader.clean_value(42), 42)

    def test_when_cleaning_value_then_comma_number_is_handled(self):
        """Tests that clean_value correctly parses a number with a comma as decimal separator."""
        self.assertEqual(self.reader.clean_value("200,5"), 200.5)

    def test_when_cleaning_value_then_invalid_percentage_is_none(self):
        """Tests that clean_value correctly parses a number with a comma as decimal separator."""
        self.assertIsNone(self.reader.clean_value("abc%"))

    def test_when_building_field_map_then_expected_mapping_is_returned(self):
        """
        Tests that _build_field_map returns the correct mapping from config.
        """
        field_map = self.reader._build_field_map()
        expected_field_map = {}
        excel_obd = self.reader._ExcelOBDReader__excel_obd
        obd_config = self.reader._ExcelOBDReader__obd_config

        for pid_name, excel_col in excel_obd.items():
            if excel_col:
                for group, fields in obd_config.items():
                    if pid_name.upper() in fields:
                        expected_field_map[excel_col] = (
                            group, fields[pid_name.upper()])
                        break
        self.assertEqual(field_map, expected_field_map)

    def test_when_creating_meta_data_record_then_expected_fields_are_set(self):
        """
        Tests that create_meta_data_record sets the correct metadata fields.
        """
        meta = self.reader.create_meta_data_record("BBN", "RESP")
        self.assertEqual(meta[MetaDataFields.FIELD_BBN_V], "BBN")
        self.assertEqual(meta[MetaDataFields.FIELD_SYS_V], "TestModel")
        self.assertEqual(meta[MetaDataFields.FIELD_SYS_N], "V123")
        self.assertEqual(meta[MetaDataFields.FIELD_SYS_M], "TestMark")
        self.assertEqual(meta[MetaDataFields.FIELD_SYS_S], "N/A")
        self.assertEqual(meta[MetaDataFields.FIELD_NET_ID], "N/A")

    def test_when_getting_messages_with_real_data_then_store_system_data_record_is_called(self):
        """
        Tests that get_messages calls store_system_data_record the expected number of times for valid data.
        """
        self.reader.get_messages()
        self.assertEqual(self.node.store_system_data_record.call_count, 7)
