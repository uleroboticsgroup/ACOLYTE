"""
This is a class-containing module.

It contains the ExcelOBDReader class, which is responsible for reading OBD-II diagnostic data
from an Excel (CSV) file and storing it as system data records on the blockchain.

IMPORTANT: The Excel file must contain OBD data from a single vehicle per session.
All rows are assumed to belong to the same car, as the session is executed for one vehicle only.
"""


import pandas as pd
import logging

from acolyte.readers.reader import Reader
from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories

from bcubed.constants.records.fields.id_value_fields import IdValueFields
from bcubed.constants.records.fields.meta_data_fields import MetaDataFields
from bcubed.constants.records.fields.system_data_fields import SystemDataFields
from bcubed.records.fields.id_uint8_value_string_field import IdUint8ValueStringField
from bcubed.records.fields.id_uint8_value_float_field import IdUint8ValueFloatField
from bcubed.records.meta_data_record import MetaDataRecord

# Index for the first row in the DataFrame; in the Excel file, this row contains vehicle/session metadata such as MODEL, VEHICLE_ID, and MARK.
FIRST_ROW_INDEX = 0

# Used to convert milliseconds to nanoseconds for timestamp consistency
NANOSECONDS_PER_MILLISECOND = 1000000


class ExcelOBDReader(Reader):
    """
    It reads OBD-II diagnostic data from an Excel (CSV) file and creates and stores the system data
    records that are generated from these rows.
    """

    __logger = logging.getLogger(__name__)

    def __init__(self, node, input_file):
        """
        Initializes the ExcelOBDReader with the given node and input file path.
        Loads the Excel file and OBD configuration.
        """
        super().__init__(node)
        self.__excel_path = input_file
        self.__data_frame = pd.read_csv(self.__excel_path).fillna('')
        self.__obd_config = AcolyteConfig().get_property(ConfigCategories.OBD)
        self.__excel_obd = AcolyteConfig().get_property("excel_obd")
        self.__float_fields = {
            SystemDataFields.FIELD_TMP_V,
            SystemDataFields.FIELD_ACT_V,
            SystemDataFields.FIELD_ACT_D,
            SystemDataFields.FIELD_IR_SE
        }
        self.__field_map = self._build_field_map()

    def _build_field_map(self):
        """
        Builds a map from the real Excel column name to (group, numeric_id).
        Only includes columns that are mapped in topics-config.yaml excel_obd and not empty.
        """
        field_map = {}
        for pid_name, excel_col in self.__excel_obd.items():
            if excel_col:
                for group, pids_dict in self.__obd_config.items():
                    if pid_name.upper() in pids_dict:
                        numeric_id = pids_dict[pid_name.upper()]
                        field_map[excel_col] = (group, numeric_id)
                        break
        return field_map

    @staticmethod
    def clean_value(value):
        """
        Cleans and converts a value from the Excel file.
        Handles string formatting, percentage values, and conversion to float if possible.
        Args:
            value: The value to clean.
        Returns:
            The cleaned value, as float or string.
        """
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
            if "%" in value:
                try:
                    return float(value.replace("%", ""))
                except ValueError:
                    return None
            try:
                return float(value)
            except ValueError:
                return value
        return value

    def create_meta_data_record(self, name: str, responsible: str):
        """
        Creates a Metadata record for Excel OBD data collection sessions.

        Uses the first row of the Excel file to extract vehicle-specific fields if available.
        Other system information fields are set to N/A as they are not available in the Excel file.
        Args:
            name (str): The black box name.
            responsible (str): The responsible system/user.
        Returns:
            MetaDataRecord: The constructed metadata record.
        """
        meta_data_record = MetaDataRecord(responsible)
        first_row = self.__data_frame.iloc[FIRST_ROW_INDEX]

        model_col = self.__excel_obd.get("model", "")
        vehicle_id_col = self.__excel_obd.get("vehicle_id", "")
        mark_col = self.__excel_obd.get("mark", "")

        meta_data_record[MetaDataFields.FIELD_BBN_V] = name
        meta_data_record[MetaDataFields.FIELD_SYS_V] = (
            "N/A" if not model_col or first_row.get(
                model_col, "") == "" else str(first_row.get(model_col, "N/A"))
        )
        meta_data_record[MetaDataFields.FIELD_SYS_S] = "N/A"
        meta_data_record[MetaDataFields.FIELD_NET_ID] = "N/A"
        meta_data_record[MetaDataFields.FIELD_OSY_T] = "N/A"
        meta_data_record[MetaDataFields.FIELD_SYS_P] = "N/A"
        meta_data_record[MetaDataFields.FIELD_SYS_N] = (
            "N/A" if not vehicle_id_col or first_row.get(
                vehicle_id_col, "") == "" else str(first_row.get(vehicle_id_col, "N/A"))
        )
        meta_data_record[MetaDataFields.FIELD_SYS_M] = (
            "N/A" if not mark_col or first_row.get(
                mark_col, "") == "" else str(first_row.get(mark_col, "N/A"))
        )

        return meta_data_record

    def get_messages(self):
        """
        Processes all rows in the Excel file and stores OBD-II data as system data records.

        For each row, iterates over the columns and, if the column matches a known OBD PID,
        creates the appropriate value field and stores the record in the blockchain.
        """
        self.__logger.info("Starting Excel OBD Reader")
        timestamp_col = self.__excel_obd.get("timestamp", "TIMESTAMP")

        for idx, row in self.__data_frame.iterrows():
            for col in row.index:
                if col in self.__field_map and pd.notna(row[col]) and row[col] != '':
                    sd_field_name, numeric_id = self.__field_map[col]
                    value = self.clean_value(row[col])
                    # Excel timestamps are in milliseconds; convert to nanoseconds for consistency
                    timestamp = int(row[timestamp_col]) * \
                        NANOSECONDS_PER_MILLISECOND

                    if sd_field_name in self.__float_fields:
                        value_field = IdUint8ValueFloatField({
                            IdValueFields.FIELD_ID: numeric_id,
                            IdValueFields.FIELD_VALUE: float(value)
                        })
                    else:
                        value_field = IdUint8ValueStringField({
                            IdValueFields.FIELD_ID: numeric_id,
                            IdValueFields.FIELD_VALUE: str(value)
                        })

                    self._create_and_store_system_data_record(
                        timestamp, sd_field_name, value_field)

                    self.__logger.info(
                        "%s (%d) @ %d -> %s: %s stored",
                        col, numeric_id, timestamp, sd_field_name, value
                    )

            self.__logger.info("Processed row %d", idx)
