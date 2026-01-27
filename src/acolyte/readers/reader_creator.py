"""
Abstract Creator for the Factory Method pattern.
"""

from abc import ABC, abstractmethod
import sys

from bcubed.blockchain.node import Node

from acolyte.readers.reader import Reader


class ReaderCreator(ABC):
    """
    Abstract class that declares the factory method.
    Contains business logic that uses Readers.
    """

    def __init__(self, node: Node, name: str, arguments):
        self._node = node
        self.__name = name
        if "responsible" in arguments:
            self.__responsible = arguments.responsible
        else:
            self.__responsible = ""

    @abstractmethod
    def factory_method(self) -> Reader:
        """
        Abstract method that subclasses must implement.
        Returns a concrete Reader instance.
        """
        pass

    def read(self) -> Reader:
        """
        Business logic method that uses the Reader product.
        This is the method that Acolyte (client) should call.

        Returns:
            Reader: The reader instance after executing get_messages()
        """
        reader = self.factory_method()
        meta_data_record = reader.create_meta_data_record(
            self.__name, self.__responsible)

        if meta_data_record is not None:
            success = self._node.store_meta_data_record(meta_data_record)
            if not success:
                sys.exit()

        reader.get_messages()

        return reader
