"""
Concrete Creator for Excel OBD readers.
"""

from acolyte.readers.reader import Reader
from acolyte.readers.reader_creator import ReaderCreator
from acolyte.readers.excel_obd_reader import ExcelOBDReader


class ExcelOBDReaderCreator(ReaderCreator):
    """
    Concrete creator that creates ExcelOBDReader instances.
    """

    def __init__(self, node, name, arguments):
        super().__init__(node, name, arguments)
        self._excel_file = arguments.input_file

    def factory_method(self) -> Reader:
        """
        Creates and returns an ExcelOBDReader instance.
        """
        return ExcelOBDReader(self._node, self._excel_file)
