"""
Concrete Creator for Operating System readers.
"""

from acolyte.readers.reader import Reader
from acolyte.readers.reader_creator import ReaderCreator
from acolyte.readers.operating_system_reader import OperatingSystemReader


class OsReaderCreator(ReaderCreator):
    """
    Concrete creator that creates OperatingSystemReader instances.
    """

    def __init__(self, node, name, responsible):
        super().__init__(node, name, responsible)

    def factory_method(self) -> Reader:
        """
        Creates and returns an OperatingSystemReader instance.
        """
        return OperatingSystemReader(self._node)
