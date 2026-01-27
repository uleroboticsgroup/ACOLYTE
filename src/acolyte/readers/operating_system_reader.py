"""
This is a class-containing module.

It contains the OperatingSystemReader class, which is responsible for reading operating
system information such as system name, memory, battery, WiFi signal, Ethernet speed and so forth.
It also creates and stores the system data records that are generated.
"""

import logging
import re
import subprocess
import time
import psutil

from bcubed.constants.records.fields.system_data_fields import SystemDataFields
from bcubed.constants.records.fields.id_value_fields import IdValueFields
from bcubed.records.fields.id_uint8_value_uint16_field import IdUint8ValueUint16Field

from bcubed.utilities.datetime_help import get_current_timestamp

from acolyte.config.acolyte_config import AcolyteConfig
from acolyte.constants.config_categories import ConfigCategories
from acolyte.constants.config_keys import ConfigKeys
from acolyte.readers.reader import Reader


class OperatingSystemReader(Reader):
    """
    It reads operating system information and creates and stores the records that are generated
    from this information.
    """

    def __init__(self, node):
        self.__system_info_retrieval = AcolyteConfig().get_property(
            ConfigKeys.SYSTEM_INFO_RETRIEVAL, ConfigCategories.TIMINGS)

        self.__logger = logging.getLogger(__name__)

        super().__init__(node)

    def create_meta_data_record(self, name: str, responsible: str):
        pass

    def get_messages(self):
        timestamp = get_current_timestamp() * 1000000
        ethernet_info = self.__get_ethernet_info()
        ram, swap = self.__get_mem_info_by_proc_meminfo()
        peripherals = self.__get_peripheral_info()

        self._create_and_store_system_data_record(
            timestamp,
            SystemDataFields.FIELD_WIFI, IdUint8ValueUint16Field({
                IdValueFields.FIELD_ID: 1,
                IdValueFields.FIELD_VALUE: ethernet_info}))
        self._create_and_store_system_data_record(
            timestamp,
            SystemDataFields.FIELD_RAM_D, str(ram))
        self._create_and_store_system_data_record(
            timestamp,
            SystemDataFields.FIELD_SWP_D, str(swap))
        self._create_and_store_system_data_record(
            timestamp,
            SystemDataFields.FIELD_PER_I, str(peripherals))

        time.sleep(self.__system_info_retrieval)

    def __get_ethernet_info(self):
        """
        Gets the ethernet speed information. If the speed is 0, the system is not connected to
        ethernet.
        """
        speed = 0

        addrs = psutil.net_if_stats()
        for addr in addrs.values():
            if addr.isup and addr.speed > 0:
                speed = addr.speed

        return speed

    def __get_mem_info_by_proc_meminfo(self):
        """
        Gets the information about the RAM memory and swap memory. It reads the information stored
        in the /proc/meminfo file.
        """
        proc_mem_info = ["MemTotal", "MemFree", "MemAvailable"]
        proc_mem_swap_info = ["SwapTotal", "SwapFree"]

        ram_memory = 0
        swap_memory = 0

        with open("/proc/meminfo", "r", encoding="utf-8") as mem_info_file:
            lines = mem_info_file.readlines()

        mem_lines_splited = [line.split(":") for line in lines]
        for mem_line_splited in mem_lines_splited:
            if mem_line_splited[0] in proc_mem_info:
                ram_memory = mem_line_splited[1].strip()
            elif mem_line_splited[0] in proc_mem_swap_info:
                swap_memory = mem_line_splited[1].strip()

        return ram_memory, swap_memory

    def __get_peripheral_info(self):
        """
        Gets the information about the connected peripherals.
        """
        devices = []

        device_re = re.compile(
            r"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        try:
            lsusb_output = subprocess.check_output("lsusb").decode("utf-8")

            for line in lsusb_output.split('\n'):
                if line:
                    info = device_re.match(line)
                    if info:
                        dinfo = info.groupdict()
                        dinfo['device'] = f"/dev/bus/usb/{dinfo.pop('bus')}/{dinfo.pop('device')}"
                        devices.append(dinfo)

        except OSError as error:
            self.__logger.error("%s", error)

        return devices
