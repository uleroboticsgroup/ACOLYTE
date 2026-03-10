"""
This is a class-containing module.

It contains the OBDReader class, which is responsible for reading OBD-II diagnostic data
from the vehicle port and storing it as system data records on the blockchain.
"""

import logging
import time
import obd

from bcubed.constants.records.fields.id_value_fields import IdValueFields
from bcubed.utilities.datetime_help import get_current_timestamp
from bcubed.records.fields.id_uint8_value_string_field import IdUint8ValueStringField
from bcubed.records.fields.id_uint8_value_float_field import IdUint8ValueFloatField
from bcubed.constants.records.fields.meta_data_fields import MetaDataFields
from bcubed.records.meta_data_record import MetaDataRecord

from acolyte.readers.reader import Reader
from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys

# Used to convert milliseconds to nanoseconds for timestamp consistency
NANOSECONDS_PER_MILLISECOND = 1000000


class OBDReader(Reader):
    """
    It reads OBD-II diagnostic data from the vehicle port and creates and stores the system data
    records that are generated from these queries.
    """

    __logger = logging.getLogger(__name__)

    # Fields that require float (the rest use string)
    FLOAT_FIELDS = {'tmpV', 'actV', 'actD', 'irSe'}

    def __init__(self, node):
        super().__init__(node)
        self.__configure_obd_settings()

        self.__logger.info("OBDReader initialized with port %s and query interval %d seconds",
                           self.__port, self.__query_interval)

    def __configure_obd_settings(self):
        """
        Loads all OBD-related configuration from the configuration file.
        """
        cfg = AcolyteConfig()
        self.__obd_config = cfg.get_property(ConfigCategories.OBD)
        self.__query_interval = cfg.get_property(
            ConfigKeys.OBD_QUERY_INTERVAL, ConfigCategories.TIMINGS)
        self.__port = cfg.get_property(
            ConfigKeys.OBD_PORT, ConfigCategories.PATHS)
        self.__baudrate = cfg.get_property(
            ConfigKeys.OBD_BAUDRATE, ConfigCategories.PATHS)
        self.__timeout = cfg.get_property(
            ConfigKeys.OBD_CONNECTION_TIMEOUT, ConfigCategories.TIMINGS)

    def __extract_value(self, resp_value):
        """Extracts clean value from pint.Quantity or returns the object."""
        return resp_value.magnitude if hasattr(resp_value, "magnitude") else resp_value

    def get_vehicle_identification(self):
        """
        Queries VIN and CALIBRATION_ID from the OBD-II interface.

        Returns:
            tuple: (vin, calibration_id) with fallback values if not available
        """
        conn = None
        vin = "SIMULATED_VIN_123456"
        calibration_id = "Generic OBD Simulator"

        try:
            conn = obd.OBD(self.__port, baudrate=self.__baudrate,
                           fast=False, timeout=self.__timeout)

            if not conn.is_connected():
                self.__logger.warning(
                    "OBD not connected. Using default values.")
                return vin, calibration_id

            # Query VIN
            vin = self.__query_vehicle_vin(conn)

            # Query CALIBRATION_ID
            calibration_id = self.__query_calibration_id(conn)

        except Exception as e:
            self.__logger.error(
                "Error connecting to OBD: %s. Using default values.", e)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        return vin, calibration_id

    def __query_vehicle_vin(self, conn):
        """
        Queries the Vehicle Identification Number from OBD.

        Args:
            conn: Active OBD connection

        Returns:
            str: VIN or default value if not available
        """
        try:
            vin_cmd = getattr(obd.commands, 'VIN', None)
            if vin_cmd is None:
                self.__logger.warning("VIN command not supported")
                return "SIMULATED_VIN_123456"

            vin_resp = conn.query(vin_cmd)
            if vin_resp.value is None:
                self.__logger.warning("VIN query returned null")
                return "SIMULATED_VIN_123456"

            # Handle different response types
            if isinstance(vin_resp.value, (bytes, bytearray)):
                vin_val = vin_resp.value.decode(
                    'utf-8', errors='ignore').strip()
            else:
                vin_val = str(vin_resp.value).strip()

            return vin_val if vin_val else "SIMULATED_VIN_123456"

        except Exception as e:
            self.__logger.error("Error querying VIN: %s", e)
            return "SIMULATED_VIN_123456"

    def __query_calibration_id(self, conn):
        """
        Queries the ECU Calibration ID from OBD.

        Args:
            conn: Active OBD connection

        Returns:
            str: Calibration ID or default value if not available
        """
        try:
            cal_cmd = getattr(obd.commands, 'CALIBRATION_ID', None)
            if cal_cmd is None:
                self.__logger.warning("CALIBRATION_ID command not supported")
                return "Generic OBD Simulator"

            cal_resp = conn.query(cal_cmd)
            if cal_resp.value is None:
                self.__logger.warning("CALIBRATION_ID query returned null")
                return "Generic OBD Simulator"

            # Handle different response types
            if isinstance(cal_resp.value, (bytes, bytearray)):
                cal_val = cal_resp.value.decode(
                    'utf-8', errors='ignore').strip()
            else:
                cal_val = str(cal_resp.value).strip()

            return cal_val if cal_val else "Generic OBD Simulator"

        except Exception as e:
            self.__logger.error("Error querying CALIBRATION_ID: %s", e)
            return "Generic OBD Simulator"

    def create_meta_data_record(self, name: str, responsible: str):
        """
        Creates a Metadata record for OBD data collection sessions.

        Vehicle-specific fields (VIN, CALIBRATION_ID) are queried from the OBD-II interface.
        System information fields are set to N/A as they are not available via standard OBD-II.
        """
        meta_data_record = MetaDataRecord(responsible)

        meta_data_record[MetaDataFields.FIELD_BBN_V] = name

        # Set vehicle system info as N/A (not available via standard OBD-II)
        meta_data_record[MetaDataFields.FIELD_SYS_V] = "N/A"
        meta_data_record[MetaDataFields.FIELD_SYS_S] = "N/A"
        meta_data_record[MetaDataFields.FIELD_NET_ID] = "N/A"
        meta_data_record[MetaDataFields.FIELD_OSY_T] = "N/A"
        meta_data_record[MetaDataFields.FIELD_SYS_P] = "N/A"

        vin, calibration_id = self.get_vehicle_identification()
        meta_data_record[MetaDataFields.FIELD_SYS_N] = vin
        meta_data_record[MetaDataFields.FIELD_SYS_M] = calibration_id

        return meta_data_record

    def get_messages(self):
        """
        Queries all PIDs defined in topics-config.yaml and stores them in BCubed.
        The mapping of PIDs to fields comes entirely from the YAML.
        """
        conn = None
        try:
            conn = obd.OBD(self.__port, baudrate=self.__baudrate,
                           fast=False, timeout=self.__timeout)
            if not conn.is_connected():
                self.__logger.warning(
                    "Not connected to OBD-II on %s", self.__port)
                return

            self.__logger.info("OBD query interval set to %d seconds",
                               self.__query_interval)

            # Flatten configuration file format: (pid_name, numeric_id, sd_field_name)
            pids_to_query = []
            for sd_field_name, pids_dict in self.__obd_config.items():
                for pid_name, numeric_id in pids_dict.items():
                    pids_to_query.append((pid_name, numeric_id, sd_field_name))

            self.__logger.info("Starting OBD queries every %d seconds (Ctrl+C to stop)...",
                               self.__query_interval)

            # Infinite loop of queries every N seconds
            while True:
                iteration_start = time.time()
                successful_queries = 0
                failed_queries = 0

                self.__logger.info("\n\n=== New round of queries ===")
                for pid_name, numeric_id, sd_field_name in pids_to_query:
                    cmd = getattr(obd.commands, pid_name, None)
                    if cmd is None:
                        self.__logger.warning("PID %s not supported", pid_name)
                        failed_queries += 1
                        continue

                    try:
                        resp = conn.query(cmd)
                        if resp is None or resp.is_null():
                            self.__logger.debug(
                                "Null response for PID %s", pid_name)
                            failed_queries += 1
                            continue

                        # Convert milliseconds to nanoseconds for timestamp consistency
                        scaled_timestamp = int(
                            get_current_timestamp()) * NANOSECONDS_PER_MILLISECOND
                        val = self.__extract_value(resp.value)

                        self.__logger.debug(
                            "PID %s (%d) = %s", pid_name, numeric_id, val)

                        # Create field according to type defined in YAML
                        if sd_field_name in self.FLOAT_FIELDS:
                            value_field = IdUint8ValueFloatField({
                                IdValueFields.FIELD_ID: numeric_id,
                                IdValueFields.FIELD_VALUE: float(val)
                            })
                        else:
                            value_field = IdUint8ValueStringField({
                                IdValueFields.FIELD_ID: numeric_id,
                                IdValueFields.FIELD_VALUE: str(val)
                            })

                        # Store in BCubed
                        self._create_and_store_system_data_record(
                            scaled_timestamp, sd_field_name, value_field)

                        self.__logger.info("%s (%d) @ %d -> %s: %s stored",
                                           pid_name, numeric_id, scaled_timestamp, sd_field_name, val)
                        successful_queries += 1

                    except Exception as e:
                        self.__logger.error(
                            "Error querying PID %s: %s", pid_name, e)
                        failed_queries += 1

                # Round summary
                iteration_duration = time.time() - iteration_start
                self.__logger.info("Round completed: %d successful, %d failed in %.2f seconds",
                                   successful_queries, failed_queries, iteration_duration)

                # Wait until N seconds have passed
                self.__logger.info(
                    "Waiting %d seconds for the next round...", self.__query_interval)
                time.sleep(self.__query_interval)

        except KeyboardInterrupt:
            self.__logger.info("Keyboard interrupt received. Exiting...")
        except Exception as e:
            self.__logger.error("Error in OBD connection: %s", e)
        finally:
            if conn:
                try:
                    conn.close()
                    self.__logger.info("OBD connection closed successfully.")
                except Exception:
                    pass
