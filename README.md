# ACOLYTE (dAta Curation fOr traceabiLity sYsTEm)
ACOLYTE is a Python application designed to facilitate traceability in autonomous systems in a cibersecure manner. It has been developed to assist in the automated extraction of data from autonomous systems. The application is available in the form of a command-line tool. Two fundamental options are available:
- Store records.
    - Reading information from a ROS bag file.
    - Reading information from the vehicle's OBD-II port.
- Get stored records by a timeframe. 

This Python application is dependant on BCubed Python library. BCubed is available at [BCubed repository](https://github.com/uleroboticsgroup/BCubed).


## :warning: Disclaimer
This Python application has only been tested in simulated blockchain environments. Using it in other environments is at your own risk. Keep possible charges in mind.


## Getting Started

### Create and activate a virtual enviroment (recommended)
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Install the requirements
```
(.venv) pip install -r requirements.txt
```

### Install BCubed Python library
Follow the instructions available in [BCubed README.md](https://github.com/uleroboticsgroup/BCubed/blob/main/README.md). It is important to note that the virtual environment has already been created.


### Install ACOLYTE
```
(.venv) $ pip install -e <acolyte_location>
```


## Execute ACOLYTE

1. Ensure the blockchain network is available.
    - (Optional) Execute an Ethereum simulator.

1. Update the configuration data in the `bcubed-config.yaml` file.

1. Configure the environment variable named BCUBED_CONF_FILE to set the `bcubed-config.yaml` path. By default, it is set to `./bcubed-config.yaml`.

### Store records

#### 1. Reading information from a ROS bag file

4. Update the configuration data in the `topics-config.yaml` file.

1. Configure the environment variable named ACOLYTE_CONF_FILE to set the `topics-config.yaml` path. By default, it is set to `./topics-config.yaml`.

1. Execute the following command:
    ```
    (.venv) $ acolyte -a store -i <rosbag2_file> -r <responsible> -w rosbag
    ```

1. To monitor operating system information too, execute the following command:
    ```
    (.venv) $ acolyte -a store -i <rosbag2_file> -r <responsible> -w rosbag -os
    ```

#### 2. Reading information from the vehicle's OBD-II port

4. Update the configuration data in the `obd-config.yaml` file.

1. Configure the environment variable named ACOLYTE_CONF_FILE to set the `obd-config.yaml` path. By default, it is set to `./topics-config.yaml`.

1. Execute the following command:
    ```
    (.venv) $ acolyte -a store -i /dev/null <responsible> -w obd
    ```

#### 3. Reading information from an Excel file with OBD-II data

4. Update the configuration data in the `obd-config.yaml` file:
    - In the `excel_obd` section, map the Excel column names to the internal OBD field names.
    - Use the exact column names from your Excel file as values.
    - Leave empty (`''`) for fields not present in your Excel.

1. Configure the environment variable named ACOLYTE_CONF_FILE to set the `obd-config.yaml` path. By default, it is set to `./topics-config.yaml`.

1. Execute the following command:
    ```
    (.venv) $ acolyte -a store -i <excel_file> -r <responsible> -w obd_excel
    ```

### Get stored records by a timeframe

1. Execute the following command:

```
(.venv) $ acolyte -a get_by_timestamp -ts <timestamp_start> -te <timestamp_end>
```


### Uninstall ACOLYTE
```
(.venv) $ pip uninstall acolyte
```

## Dataset available
A dataset has been created to facilitate testing of the application without the need to create your own rosbag. It is available at the following URL: [https://zenodo.org/records/16630061](https://zenodo.org/records/16630061).


## Acknowledgements

This research is part of the project TESCAC, financed by “European Union NextGeneration-EU, the Recovery Plan, Transformation and Resilience, through INCIBE".

<p align="center">
  <img src="./docs/INCIBE.jpg" width="100%" />
</p>
