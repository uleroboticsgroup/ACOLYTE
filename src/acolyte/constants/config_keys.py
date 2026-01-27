"""
This is a class-containing module.

It contains the Keys class, which includes only constants related to configuration keys.
These constants define the keys that the configuration can contain.
"""


class ConfigKeys:  # pylint: disable=too-few-public-methods
    """
    It contains only constants related to config keys. These constants define the keys that the
    config file can contain.
    Add values as required.
    """

    DAEMON_WORKING_DIR = "daemon_working_dir"
    DAEMON_PID_FILE = "daemon_pid_file"
    SYSTEM_INFO_RETRIEVAL = "system_info_retrieval"
    ROSBAG_READING_RETRY = "rosbag_reading_retry"
    OBD_QUERY_INTERVAL = "obd_query_interval"
    OBD_PORT = "obd_port"
    OBD_BAUDRATE = "obd_baudrate"
    OBD_CONNECTION_TIMEOUT = "obd_connection_timeout"
