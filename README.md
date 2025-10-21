# ACOLYTE (dAta Curation fOr traceabiLity sYsTEm)
ACOLYTE is a Python application designed to facilitate traceability in autonomous systems in a cibersecure manner. It has been developed to assist in the automated extraction of data from autonomous systems. The application is available in the form of a command-line tool. Two fundamental options are available:
- Store records from a rosbag2 file. 
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


### Execute ACOLYTE
1. Ensure the blockchain network is available.
   - (Optional) Execute an Ethereum simulator.

1. Update the configuration data in the config.yaml file.

1. Update the configuration data in the topics-config.yaml file.

#### Store records that are created by reading topic messages from a rosbag2 file
```
(.venv) $ acolyte -a store -i <rosbag2_file> -r <responsible> -w rosbag
```

#### Store records that are created by reading topic messages from a rosbag2 file and monitoring the operating system
```
(.venv) $ acolyte -a store -i <rosbag2_file> -r <responsible> -w rosbag -os
```

#### Get stored records by a timeframe
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