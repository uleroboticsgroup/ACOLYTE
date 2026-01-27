"""
Concrete Creator for OBD readers.
"""

from acolyte.readers.reader import Reader
from acolyte.readers.reader_creator import ReaderCreator
from acolyte.readers.obd_reader import OBDReader


class OBDReaderCreator(ReaderCreator):
    """
    Concrete creator that creates OBDReader instances.
    """

    def __init__(self, node, name, arguments):
        super().__init__(node, name, arguments)

    def factory_method(self) -> Reader:
        """
        Creates and returns an OBDReader instance.
        """
        return OBDReader(self._node)
