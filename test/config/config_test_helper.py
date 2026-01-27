"""
This is a class-containing module.

It contains the ConfigTestHelper class, which is responsible for configuring the AcolyteConfig
instance to be used in tests, according to the needs of each test.
"""

import os
from pathlib import Path

from test.config.constants import (
    CONF_FILE_NAME,
    VALUE_1,
    VALUE_2,
    VALUE_3
)

import yaml

from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys
from bcubed.constants.records.fields.system_data_fields import SystemDataFields


class ConfigTestHelper():
    """
    Provides a common configuration for the AcolyteConfig instance to be used in the tests. This
    way there is no duplicate code in each test that needs the AcolyteConfig instance. It also
    cleans up the singleton instance to provide a clean start.
    """

    def __init__(self) -> None:
        self.__previous_conf_file = os.environ.get("ACOLYTE_CONF_FILE", "")
        self.__set_test_environment_variable()

        AcolyteConfig.clear()

    def __set_test_environment_variable(self):
        if "ACOLYTE_CONF_FILE" in os.environ:
            os.environ["ACOLYTE_CONF_FILE"] = CONF_FILE_NAME
        else:
            os.environ.setdefault("ACOLYTE_CONF_FILE", CONF_FILE_NAME)

    def create_test_config_file(self):
        """
        Creates a yaml configuration file with the categories, keys and values needed to set up
        ACOLYTE.
        Add categories, keys and values as required.
        """

        config_dict = {
            ConfigCategories.PATHS: {
                ConfigKeys.DAEMON_WORKING_DIR: "./os_daemon/",
                ConfigKeys.DAEMON_PID_FILE: "./os_daemon/os_daemon.pid",
                ConfigKeys.OBD_PORT: '/dev/ttyUSB0',
                ConfigKeys.OBD_BAUDRATE: 115200
            },
            ConfigCategories.TIMINGS: {
                ConfigKeys.SYSTEM_INFO_RETRIEVAL: 0,
                ConfigKeys.ROSBAG_READING_RETRY: 0,
                ConfigKeys.OBD_QUERY_INTERVAL: 10,
                ConfigKeys.OBD_CONNECTION_TIMEOUT: 30
            },
            ConfigCategories.TOPICS: {
                "/global_costmap/costmap_raw": 1,
                "/head_front_camera/rgb/image_raw": 2,
                "/joy_priority": 3,
                "/local_costmap/voxel_grid": 4,
                "/local_costmap/costmap": 5,
                "/local_costmap/clearing_endpoints": 6,
                "/local_costmap/published_footprint": 7,
                "/map": 8,
                "/mobile_base_controller/odom": 9,
                "/power/is_emergency": 10,
                "/rosout": 11,
                "/scan_raw": 12
            },
            ConfigCategories.OBD: {
                SystemDataFields.FIELD_SYS_X: {
                    "BAROMETRIC_PRESSURE": 1,
                    "COMMANDED_EQUIV_RATIO": 2,
                    "CVN": 3,
                    "DISTANCE_SINCE_DTC_CLEAR": 4,
                    "ENGINE_LOAD": 5,
                    "EVAP_VAPOR_PRESSURE": 6,
                    "FREEZE_DTC": 7,
                    "FUEL_LEVEL": 8,
                    "FUEL_PRESSURE": 9,
                    "GET_CURRENT_DTC": 10,
                    "LONG_FUEL_TRIM_1": 11,
                    "MAF": 12,
                    "O2_S1_WR_CURRENT": 13,
                    "O2_S1_WR_VOLTAGE": 14,
                    "OBD_COMPLIANCE": 15,
                    "RPM": 16,
                    "SHORT_FUEL_TRIM_1": 17,
                    "SPEED": 18,
                    "STATUS": 19,
                    "STATUS_DRIVE_CYCLE": 20,
                    "TIME_SINCE_DTC_CLEARED": 21,
                    "TIMING_ADVANCE": 22,
                    "WARMUPS_SINCE_DTC_CLEAR": 23
                },
                SystemDataFields.FIELD_TMP_V: {
                    "CATALYST_TEMP_B1S1": 1,
                    "COOLANT_TEMP": 2,
                    "INTAKE_TEMP": 3
                },
                SystemDataFields.FIELD_ACT_D: {
                    "COMMANDED_EGR": 1
                },
                SystemDataFields.FIELD_ACT_V: {
                    "EGR_ERROR": 1,
                    "THROTTLE_POS": 2
                },
                SystemDataFields.FIELD_IR_SE: {
                    "O2_B1S1": 1,
                    "O2_B1S2": 2
                }
            }
        }

        self.__dump_config_file_json(config_dict)

    def create_fake_config_file(self):
        """
        Creates a yaml configuration file with fake values, just to test that the AcolyteConfig class
        works as expected.
        """

        config_dict = {
            VALUE_1: {
                VALUE_2: VALUE_3
            }
        }

        self.__dump_config_file_json(config_dict)

    def __dump_config_file_json(self, config_dict: dict):
        conf_file = Path(CONF_FILE_NAME).resolve()
        with open(conf_file, "w", encoding="utf-8") as file:
            yaml.dump(config_dict, file)

    def tear_down(self):
        """
        Performs the TearDown actions on the AcolyteConfig instance. Removes the configuration file, if it
        exists; sets the previous value of the ACOLYTE_CONF_FILE environment variable; and removes
        the contract json file, if it exists.
        """

        conf_file = Path(CONF_FILE_NAME)
        if conf_file.exists():
            os.remove(CONF_FILE_NAME)

        os.environ["ACOLYTE_CONF_FILE"] = self.__previous_conf_file
