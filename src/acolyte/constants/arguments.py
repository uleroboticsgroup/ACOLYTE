"""
This is a class-containing module.

It contains the Arguments class, which contains only constants related to argument options.
"""


class Arguments:  # pylint: disable=too-few-public-methods
    """
    It contains only constants related to arguments.
    Add values as required.
    """

    # -a, --action
    ACTION_STORE = "store"
    ACTION_GET_BY_TIMESTAMP = "get_by_timestamp"

    # -w, --way
    WAY_ROSBAG = "rosbag"
    WAY_TOPICS = "topics"
    WAY_OBD = "obd"
