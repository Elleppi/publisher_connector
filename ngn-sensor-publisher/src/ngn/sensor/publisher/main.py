from logging import config

from constants import LOGGING_CONFIGURATION
from sensor_publisher import SensorPublisher

config.dictConfig(LOGGING_CONFIGURATION)


def main():
    sensor_publisher = SensorPublisher()
    sensor_publisher.initialise()
    sensor_publisher.start()


if __name__ == "__main__":
    main()
