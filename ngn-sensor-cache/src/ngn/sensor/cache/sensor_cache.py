import base64
import csv
import json
import logging
import os
import sys
from queue import Queue
from threading import Thread
from time import sleep
from typing import List

import constants as cnt
import requests
from redis_connector import RedisConnector

log = logging.getLogger(__name__)


class SensorCache:
    def __init__(self):
        self._redis_connector = RedisConnector()
        self._caching_queue: Queue = Queue()
        self._sensor_info_endpoint: str = None
        self._cache_ttl: int = None
        self._headers: dict = None

    def _populate_cache_with_csv(self):
        """Populate the Cache with initial values.
        It reads the sensor info from a CSV and stores it into Redis.
        """

        log.info("Populating cache with CSV info...")
        # Open the CSV file and read its contents
        with open(cnt.SENSOR_METADATA_CSV, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)  # Create a CSV reader object
            for row in csv_reader:
                sensor_key = row.get(cnt.SENSOR_KEY)
                building_name = row.get(cnt.BUILDING_NAME)
                if not (sensor_key and building_name):
                    continue

                room_name = row.get(cnt.ROOM_NAME)
                floor_name = row.get(cnt.FLOOR_NAME)
                object_name = row.get(cnt.OBJECT_NAME)
                service_type = row.get(cnt.SERVICE_TYPE)
                measurement_type = row.get(cnt.MEASUREMENT_TYPE)
                unit_of_measure = row.get(cnt.UNIT_OF_MEASURE)

                house_number = None
                for (
                    house_mapping_name,
                    building_mapping_name,
                ) in cnt.BUILDING_NAMES.items():
                    if building_mapping_name == building_name:
                        house_number = house_mapping_name
                        break

                sensor_name = house_number + "_"
                if floor_name:
                    sensor_name += floor_name + "_"
                if room_name:
                    sensor_name += room_name + "_"
                if service_type:
                    sensor_name += service_type + "_"
                if object_name:
                    sensor_name += object_name + "_"
                if measurement_type:
                    sensor_name += measurement_type

                sensor_info_dict = {
                    cnt.SENSOR_KEY: sensor_key,
                    cnt.SENSOR_NAME: sensor_name,
                    cnt.BUILDING_NAME: building_name,
                    cnt.ROOM_NAME: room_name or "",
                    cnt.FLOOR_NAME: floor_name or "",
                    cnt.SERVICE_TYPE: service_type or "",
                    cnt.OBJECT_NAME: object_name or "",
                    cnt.MEASUREMENT_TYPE: measurement_type or "",
                    cnt.UNIT_OF_MEASURE: unit_of_measure or "",
                }

                log.debug("Storing sensor info %s...", sensor_info_dict)
                self._redis_connector.store(key=sensor_key, value=sensor_info_dict)

        log.info("Cache populated successfully")

    def initialise(self):
        """Initialise this object's variables and populate the cache with initial values."""

        log.info("Initialising Sensor Cache...")
        self._sensor_info_endpoint = os.getenv("CONNECTOR_SOURCE_API_URL")
        source_api_username = os.getenv("SOURCE_API_USERNAME")
        source_api_password = os.getenv("SOURCE_API_PASSWORD")

        credentials = f"{source_api_username}:{source_api_password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        self._headers = {"Authorization": f"Basic {encoded_credentials}"}

        cache_ttl_str = os.getenv("CACHE_TTL")
        try:
            cache_ttl = int(cache_ttl_str)
        except ValueError:
            log.error(
                "Environment variable 'CACHE_TTL' is not an integer: %s", cache_ttl_str
            )
            sys.exit(1)
        else:
            self._cache_ttl = cache_ttl

        self._populate_cache_with_csv()
        log.info("Sensor Cache initialised")

    @staticmethod
    def get_sensor_metadata(endpoint: str, headers: dict) -> List[dict]:
        """Use the 'requests' method to make a GET call to the GIRA Home Server endpoint
        to retrieve sensors metadata.

        Args:
            endpoint (str): the GIRA Home Server endpoint.
            headers (dict): includes the credentials to make the query.

        Returns:
            List[dict]: list of items representing sensor info.
        """

        log.debug("Calling endpoint %s...", endpoint)

        try:
            endpoint_response = requests.get(endpoint, headers=headers, verify=False)
        except Exception as ex:
            log.exception("Got an exception in get_sensor_metadata: %s", ex)
            return {}

        endpoint_response_dict = {}
        try:
            endpoint_response_dict: dict = endpoint_response.json()
        except json.decoder.JSONDecodeError as ex:
            log.info("Error decoding %s: %s", endpoint_response_dict, ex)
            endpoint_response_dict = {}

        sensor_info_data: dict = endpoint_response_dict.get("data", {})
        sensor_info_items: List[dict] = sensor_info_data.get("items", [])

        log.info(
            "Returned %d sensor info from sensor metadata endpoint",
            len(sensor_info_items),
        )

        return sensor_info_items

    @staticmethod
    def _parse_sensor_name(sensor_key: str, sensor_name: str) -> dict:
        """Parses the sensor name to retrieve specific info about the sensor metadata.

        Args:
            sensor_key (str): sensor key.
            sensor_name (str): the long representation of sensor info.

        Returns:
            dict: the sensor metadata in a dictionary format.
        """

        if not sensor_name.lower().startswith("house"):
            log.debug(
                "Bad format of Sensor Key '%s' and/or Sensor Name '%s'",
                sensor_key,
                sensor_name,
            )
            return {}

        description_list = sensor_name.split("_")

        floor_name = room_name = service_type = object_name = ""

        if description_list[1].startswith("Floor"):
            floor_name = description_list[1]
            service_type = description_list[3]
            room_name = description_list[2] if len(description_list) > 4 else ""
            object_name = description_list[4] if len(description_list) > 4 else ""
        else:
            room_name = description_list[1] if len(description_list) > 4 else ""
            service_type = (
                description_list[2]
                if len(description_list) > 4
                else description_list[1]
            )
            object_name = (
                description_list[3]
                if len(description_list) > 4
                else description_list[2]
            )

        if description_list[-1] == object_name:
            object_name = ""

        if "weather" in sensor_name.lower():
            building_name = cnt.WEATHER_STATION_HOUSE_NUMBER
        else:
            building_name = description_list[0]

        sensor_info_dict = {
            cnt.SENSOR_KEY: sensor_key,
            cnt.SENSOR_NAME: sensor_name,
            cnt.BUILDING_NAME: building_name,
            cnt.ROOM_NAME: room_name,
            cnt.FLOOR_NAME: floor_name,
            cnt.SERVICE_TYPE: service_type,
            cnt.OBJECT_NAME: object_name,
            cnt.MEASUREMENT_TYPE: description_list[-1],
        }

        return sensor_info_dict

    def _cache_sensor_info_store(self):
        """Thread continuously waiting for sensor info from a queue.
        It parses and stores the sensor metadata into the cache.
        """

        while True:
            sensor_info: dict = self._caching_queue.get()
            log.debug("Received new sensor info from queue: %s", sensor_info)

            sensor_key: str = sensor_info.get("key")
            if not sensor_key:
                log.debug("Missing Sensor Key. Skipping sensor")
                continue

            sensor_meta: dict = sensor_info.get("meta", {})
            sensor_name: str = sensor_meta.get("description")

            sensor_metadata = {}
            try:
                sensor_metadata = self._parse_sensor_name(sensor_key, sensor_name)
            except KeyError as e:
                log.exception(
                    "Sensor name '%s' not conform with the expected structure: %s",
                    sensor_name,
                    e,
                )
                continue

            if not sensor_metadata:
                continue

            # Check if this sensor is already stored in cache
            existing_sensor_info = self._redis_connector.get(key=sensor_key)
            if existing_sensor_info:
                # Update the cache entry with updated data
                log.debug("Updating Sensor Info with updated values...")
                existing_sensor_info.update(sensor_metadata)
                self._redis_connector.store(key=sensor_key, value=existing_sensor_info)
            else:
                # Store the sensor info in cache for the first time
                log.debug("Storing sensor info for the first time: %s", sensor_metadata)
                sensor_metadata.update({cnt.UNIT_OF_MEASURE: ""})
                self._redis_connector.store(key=sensor_key, value=sensor_metadata)

            log.debug("Sensor Info stored to cache")

    def _cache_sensor_info_get(self):
        """Thread that periodically fetches updated sensor info from the Gira Home Server
        and adds the info of each sensor in a queue.
        """

        while True:
            from_param = 0
            sensor_info_items = []

            while True:
                log.debug("Getting new sensor info from server...")
                inner_url = self._sensor_info_endpoint + "&from=" + str(from_param)
                try:
                    sensor_info_items = self.get_sensor_metadata(
                        endpoint=inner_url, headers=self._headers
                    )
                except Exception as ex:
                    log.exception(
                        "Raised an exception in cache_sensor_info_get: %s", ex
                    )
                    break

                # If response is empty, we've got all sensors, and need to break the loop
                if not sensor_info_items:
                    break

                from_param += 1000

                for sensor_info in sensor_info_items:
                    self._caching_queue.put(sensor_info)

            sleep(5)

    def start(self):
        """Entry point of this class. It starts the thread to receive sensor info from a queue
        and the loop to periodically fetch new sensor info from the Gira Home Server and add them to the queue.
        """

        log.info("Starting caching store thread...")
        Thread(
            target=self._cache_sensor_info_store, name="cache_sensor_info_store"
        ).start()
        log.info("Caching store thread started")

        self._cache_sensor_info_get()
