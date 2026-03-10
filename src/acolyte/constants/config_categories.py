"""
This is a class-containing module.

It contains the Categories class, which includes only constants related to configuration categories.
These constants define the categories that the configuration can contain.
"""


class ConfigCategories:  # pylint: disable=too-few-public-methods
    """
    It contains only constants related to config categories. These constants define the categories
    that the config file can contain.
    Add values as required.
    """

    PATHS = "paths"
    TOPICS = "topics"
    TIMINGS = "timings"
    OBD = "obd"
    EXCEL_OBD = "excel_obd"
