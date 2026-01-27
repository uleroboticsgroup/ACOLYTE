"""
This is a class-containing module.

It contains the Reader class, which serves as the base class for all Readers and encompasses
their shared functions.
"""

import sys

from abc import ABC, abstractmethod

from bcubed.blockchain.node import Node
from bcubed.constants.records.fields.system_data_fields import SystemDataFields
from bcubed.records.system_data_record import SystemDataRecord


class Reader(ABC):
    """
    It contains the base class for all the Readers.
    """

    def __init__(self, node: Node):
        self._node = node

    @abstractmethod
    def get_messages(self):
        """
        Gets the data to store as record.
        Must be implemented by each concrete Reader.
        """
        pass

    @abstractmethod
    def create_meta_data_record(self, name: str, responsible: str):
        """
        Creates a meta data record with the provided information.
        Must be implemented by each concrete Reader.
        """
        pass

    def _create_and_store_system_data_record(self, timestamp: int, nam_f: str, val_f):
        """
        Creates and stores a system data record with the provided information.
        """

        system_data_record = SystemDataRecord()

        system_data_record[SystemDataFields.FIELD_SYS_T] = timestamp
        system_data_record[nam_f] = val_f

        try:
            self._node.store_system_data_record(system_data_record)
        except SystemExit:
            sys.exit()
