from logging import config

from constants import LOGGING_CONFIGURATION
from sensor_cache import SensorCache

config.dictConfig(LOGGING_CONFIGURATION)


def main():
    sensor_cache = SensorCache()
    sensor_cache.initialise()
    sensor_cache.start()


if __name__ == "__main__":
    main()
