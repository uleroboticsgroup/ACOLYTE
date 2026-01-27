"""
This is a class-containing module.

It contains the OperatingSystemStaticInfo class, which is responsible for reading operating
system information such as system name, memory, battery, WiFi signal, Ethernet speed and so forth.
It also creates and stores the system data records that are generated.
"""

import platform


class OperatingSystemStaticInfo():
    """
    It reads operating system information and creates and stores the records that are generated
    from this information.
    """

    def get_system_name(self):
        """
        Returns the system/OS name.
        """

        return platform.system()

    def get_release_version(self):
        """
        Returns the system/OS release and version.
        """

        return platform.release() + " " + platform.version()

    def get_serial_number(self):
        """
        Returns the system/OS serial number.
        """

        # TODO: Find a way to obtain serial number.

        return "0000000000000000"

    def get_vendor_id(self):
        """
        Returns the system/OS vendor ID.
        """

        with open("/proc/cpuinfo", "r", encoding="utf-8") as cpu_info_file:
            info = cpu_info_file.readlines()

        vendor_id = [value.strip().split(":")[1]
                     for value in info if "vendor_id" in value]

        return vendor_id[0].strip()

    def get_network_name(self):
        """
        Returns the network name.
        """

        return platform.node()

    def get_operating_system_type(self):
        """
        Returns the operating system type.
        """

        return platform.machine()

    def get_system_processors(self):
        """
        Returns the processors system information.
        """

        processors = {}

        with open("/proc/cpuinfo", "r", encoding="utf-8") as cpu_info_file:
            info = cpu_info_file.readlines()

        cpuinfo = [
            value.strip().split(":")[1] for value in info if "model name" in value
        ]
        for index, item in enumerate(cpuinfo):
            processors[str(index)] = item

        return str(processors)
