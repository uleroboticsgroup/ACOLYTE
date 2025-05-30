"""
This is a multi-class module.

It contains the SingletonMeta class, which is a metaclass that supports the Singleton pattern and 
ensures that only one instance of the same class is created when it is inherited.

It also contains the Config class, which inherits from the SingletonMeta class and is responsible
for configuration. It reads the configuration file and retrieves and stores the property values.
"""

import logging
import os
import yaml


ENCODING = "utf-8"
READ_MODE = "r"
WRITE_MODE = "w"

ACOLYTE_CONF_FILE = 'ACOLYTE_CONF_FILE'


class SingletonMeta(type):
    """
    It contains all the single instances of the classes that inherits from it. It ensures that only
    one instance of the same class is created.
    """

    __instances = {}

    def __call__(cls, *args, **kwargs):
        """
        """

        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]

    def clear(cls):
        """
        ONLY FOR TESTING PURPOSES. Do not use.
        """

        cls.__instances.clear()


class Config(metaclass=SingletonMeta):
    """
    It contains a dictionary of all the properties stored in the yaml configuration file. If the
    configuration file does not exist, an empty one is created by default. It also allows to get
    and set properties.
    """

    __logger = logging.getLogger(__name__)

    __config = {}

    def __init__(self) -> None:
        self.__read_configuration_file()

        self.__logger.info("%s is initialized.", __class__.__name__)

    def __read_configuration_file(self):
        self.__conf_file = os.environ.get(
            ACOLYTE_CONF_FILE, "topics-config.yaml")

        if os.path.exists(self.__conf_file) is False:
            self.__logger.error(
                "%s file does not exist. A default empty one will be created.", self.__conf_file)
            return

        with open(self.__conf_file, READ_MODE, encoding=ENCODING) as file:
            try:
                config_dict = yaml.load(file, Loader=yaml.SafeLoader)
                for key in config_dict:
                    self.__config[key] = config_dict[key]

            except yaml.YAMLError as ex:
                self.__logger.error("%s", ex)

    def get_property(self, name: str, category: str = ""):
        """
        It returns the value of the property name. If the category is passed, then it searches for
        the property within the given category. If the property does not exist, it returns None.
        """

        if category != "" and category is not None:
            if category not in self.__config:
                return None

            if name not in self.__config[category]:
                return None

        elif name not in self.__config:
            return None

        if (category != "" and category is not None):
            return self.__config[category][name]

        return self.__config[name]

    def set_property(self, name: str, value: str, category: str = ""):
        """
        It stores the value in the property name. If the category is passed, then it stores the
        property and the value within the given category. If an exception is thrown the value is
        not stored.
        """

        if os.path.exists(self.__conf_file) is True:
            with open(self.__conf_file, READ_MODE, encoding=ENCODING) as file:
                try:
                    config_dict = yaml.load(file, Loader=yaml.SafeLoader)
                except yaml.YAMLError as ex:
                    self.__logger.error("%s", ex)
                    return
        else:
            config_dict = {}

        if (category != "" and category is not None):
            config_dict[category][name] = value
        else:
            config_dict[name] = value

        with open(self.__conf_file, WRITE_MODE, encoding=ENCODING) as file:
            yaml.dump(config_dict, file)
            if (category != "" and category is not None):
                self.__config[category][name] = value
            else:
                self.__config[name] = value

        self.__logger.info(
            "The value '%s' has been stored in property '%s' and category '%s'", value, name, category)
