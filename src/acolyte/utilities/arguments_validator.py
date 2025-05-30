"""
This is a class-containing module.

It contains the ArgumentsValidator class, which is responsible for the arguments validation.
"""

import logging
import os

from acolyte.constants.rosbag_files import RosBagFileExtensions


class ArgumentsValidator:
    """
    It contains all the arguments validations needed to the performance of the program.
    """

    __logger = logging.getLogger(__name__)

    def __init__(self, arguments):
        self.__arguments = arguments

    def validate_arguments(self):
        """
        Returns if all the arguments are valid.
        """
        are_valid = True

        if self.__arguments.action == 'store':
            are_valid = are_valid and self.__is_valid_input_file(
                self.__arguments.input_file)
            are_valid = are_valid and self.__is_valid_responsible_name(
                self.__arguments.responsible)

        return are_valid

    def __is_valid_input_file(self, input_file: str):
        if input_file is not (None and "") and os.path.exists(input_file):
            input_file_splitted = input_file.split(".")
            extension = input_file_splitted[len(input_file_splitted) - 1]

            if extension == RosBagFileExtensions.DB3 or extension == RosBagFileExtensions.MCAP:
                return True

        self.__logger.critical(
            "The input file is not valid. Please, review it.")

        return False

    def __is_valid_responsible_name(self, responsible_name: str):
        if responsible_name is not (None and ""):
            return True

        self.__logger.critical(
            "The responsible name is not valid. Please, review it.")

        return False

    def get_arguments(self):
        """
        Returns the arguments.
        """
        return self.__arguments
