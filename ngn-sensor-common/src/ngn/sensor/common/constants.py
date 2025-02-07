import os

SENSOR_NAME = "sensor_name"
SENSOR_KEY = "sensor_key"
BUILDING_NAME = "building_name"
FLOOR_NAME = "floor_name"
ROOM_NAME = "room_name"
SERVICE_TYPE = "service_type"
OBJECT_NAME = "object_name"
MEASUREMENT_TYPE = "measurement_type"
LAST_SHARED_VALUE = "last_shared_value"
UNIT_OF_MEASURE = "unit_of_measure"
LAST_SHARED_DATETIME = "last_shared_datetime"

WEATHER_STATION_HOUSE_NUMBER = "House 10"
BUILDING_NAMES = {
    "House 1": "1910s Terrace Left",
    "House 2": "1910s Terrace Mid",
    "House 3": "1910s Terrace Right",
    "House 4": "1930s Semi-Detached Left",
    "House 5": "1930s Semi-Detached Right",
    "House 6": "1950s Bungalow",
    "House 7": "1970s Ground Floor Flat",
    "House 8": "1970s First Floor Flat",
    "House 9": "1990s Detached",
    WEATHER_STATION_HOUSE_NUMBER: "Weather Stations",
}

INITIAL_SUBSCRIPTION_PAYLOAD = {
    "type": "subscribe",
    "param": {"keys": ["CO@*"], "context": "iotics-connector-cev"},
}

SENSOR_METADATA_CSV = "sensor_metadata.csv"

# Logging Configurations
logging_level = os.getenv("LOGGING_LEVEL")
LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(asctime)s] [%(module)s] %(levelname)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": logging_level,
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"level": logging_level, "handlers": ["console"]},
}
