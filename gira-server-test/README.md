
# PublisherSimulator 

## Overview

The `PublisherSimulator` simulates a data publisher for sensor systems.


## Key Methods

### `__init__(self, data_source: DataSource)`
- Initializes the simulator with a data source.


### `initialise(self)`
-  Sets up the simulator, including identity and API. Starts a background thread for automatic token refresh.

### `_setup_twin_structure(self, sensor_description: str, sensor_key: str) -> TwinStructure`
-  Configures the twin structure with properties, location, and feeds.

### `_create_twin(self, twin_structure: TwinStructure, sensor_key: str) -> str`
-  Creates a digital twin and registers it with the IoT platform.


### `_share_data(self, twin_did: str, feed_id: str, min_value: int, max_value: int, frequency: int)`
-  Continuously generates and shares data samples via the specified twin and feed.

### `_start_sharing_data(self, twin_structure: TwinStructure, twin_did: str, min_value: int, max_value: int, frequency: int)`
-  Starts data-sharing processes for each feed using separate threads.


### `start(self)`
-  Reads sensor data from a CSV file, creates digital twins, and initiates data sharing.
- **Details**: 
  - Reads sensor data from a CSV file.
  - Configures and creates twins.
  - Starts data-sharing threads and manages sensor limits per house.
  - Waits for threads to complete before finishing.

## CSV File Format

- **File Name**: Configured in `constant.RESILIENCE_STATS_FILENAME`.
- **Columns**: 
  - `sensor_description`: Description of the sensor.
  - `sensor_key`: Unique key for the sensor.
  - `min`: Minimum value for readings.
  - `max`: Maximum value for readings.


## Constants

The following constants are used in the `PublisherSimulator` class to configure various aspects of the simulation, including sensor data generation, feed properties, and metadata.

### General Constants

- **`RESILIENCE_STATS_FILENAME`**: The name of the CSV file containing sensor data. 

### Sensor Properties

- **`PROPERTY_KEY_LABEL`**: The key used for the sensor label property. Value: `"label"`.
- **`PROPERTY_KEY_COMMENT`**: The key used for the sensor comment property. Value: `"comment"`.
- **`PROPERTY_KEY_CREATED_BY`**: The key used for the creator property. Value: `"created_by"`.
- **`SIMULATOR_CREATED_BY_VALUE`**: The value assigned to the creator property.


### Feed IDs

- **`SIMULATOR_FEED_ID`**: The identifier for the feed used in the Sensor Twin. Value: `"feed_id"`.

### Feed Properties

- **`SIMULATOR_VALUE_LABEL`**: The label for the feed used in the Sensor Twin. Value: `"sensor_feed"`.
- **`SIMULATOR_FEED_DATATYPE`**: The data type of the feed. 

### Location Constants

- **`INTEGREL_LAT`**: The latitude coordinate for the sensor location. Value: `52.0` (or other relevant value).
- **`INTEGREL_LON`**: The longitude coordinate for the sensor location. Value: `-1.0` (or other relevant value).

### Data Sharing Configuration

- **`SENSOR_SHARING_FREQUENCY`**: List of possible frequencies (in seconds) at which data samples are generated and shared. 
- **`SAMPLES_PER_HOUSE`**: Maximum number of sensors allowed per house. 



## Commands

- **Run simulator_connector:**
  ```sh
  make ngn-simulator-run
  ```

- **Run simulator_connector in detached mode:**
  ```sh
  make ngn-simulator-run-detached
  ```

- **View logs for simulator_connector:**
  ```sh
  make ngn-simulator-logs
  ```

- **Stop simulator_connector:**
  ```sh
  make ngn-simulator-down
  ```

