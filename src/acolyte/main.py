"""
This is the main file.
"""

import argparse
import sys

from bcubed.bcubed import BCubed
from bcubed.utilities.datetime_help import get_current_timestamp

from acolyte.acolyte import Acolyte
from acolyte.utilities.arguments_validator import ArgumentsValidator


def parse_arguments():
    """
    Parses command line strings into Python objects.
    """

    parser = argparse.ArgumentParser(description=__doc__)

    # Global
    required_argument_group = parser.add_argument_group(
        "required named arguments")

    required_argument_group.add_argument(
        "-a",
        "--action",
        required=True,
        choices=["store", "get_by_timestamp"],
        help="get or store data"
    )

    # Store
    store_argument_group = parser.add_argument_group(
        "store arguments")

    store_argument_group.add_argument(
        "-i",
        "--input_file",
        required='store' in sys.argv,
        help="input file log path to read from",
    )

    store_argument_group.add_argument(
        "-r",
        "--responsible",
        required='store' in sys.argv,
        help="name of the system responsible"
    )

    store_argument_group.add_argument(
        "-w",
        "--way",
        default="rosbag",
        choices=["rosbag", "obd", "obd_excel"],
        required='store' in sys.argv,
        help="way to read data",
    )

    store_argument_group.add_argument(
        "-os",
        "--operating_system",
        action="store_true",
        help="operating system monitoring",
    )

    # Get by timestamp
    get_by_timestamp_group = parser.add_argument_group(
        "get by timestamp arguments")

    get_by_timestamp_group.add_argument(
        "-ts",
        "--timestamp-start",
        default=0,
        help="the start datetime to get",
    )

    get_by_timestamp_group.add_argument(
        "-te",
        "--timestamp-end",
        default=get_current_timestamp(),
        help="the end datetime to get",
    )

    return parser.parse_args()


def main():
    """
    Main function.
    """

    arguments = parse_arguments()

    arguments_validator = ArgumentsValidator(arguments)
    are_valid = arguments_validator.validate_arguments()

    try:
        if are_valid:
            bcubed = BCubed()
            acolyte = Acolyte(bcubed)

            acolyte.run(arguments)
            acolyte.stop(arguments)

    except KeyboardInterrupt:
        acolyte.stop(arguments)
        sys.exit()


if __name__ == "__main__":
    main()
