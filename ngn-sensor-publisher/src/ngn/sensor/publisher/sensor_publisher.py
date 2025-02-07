import base64
import json
import logging
import os
import ssl
from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep

import constants as cnt
from confluent_kafka import Producer
from redis_connector import RedisConnector
from websocket import WebSocketException, create_connection

log = logging.getLogger(__name__)


class SensorPublisher:
    def __init__(self):
        self._redis_connector = RedisConnector()
        self._sensor_data_queue: Queue = Queue()
        self._headers: dict = None
        self._source_api_ws_url: str = None
        self._kafka_conf: dict = {}

    def initialise(self):
        """Initialising the Sensor Publisher connector by creating an 'Application'
        that connects to the Kafka cluster.
        """

        log.info("Initialising Sensor Publisher Connector...")
        kafka_broker_address = os.getenv("KAFKA_BROKER_ADDRESS")
        kafka_broker_sasl_port = os.getenv("KAFKA_BROKER_SASL_PORT")
        kafka_broker_sasl_username = os.getenv("KAFKA_SASL_USERNAME")
        kafka_broker_sasl_password = os.getenv("KAFKA_SASL_PASSWORD")
        kafka_broker_ca_certificate = os.getenv("KAFKA_CA_CERTIFICATE")

        self._kafka_conf = {
            "bootstrap.servers": f"{kafka_broker_address}:{kafka_broker_sasl_port}",
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": kafka_broker_sasl_username,
            "sasl.password": kafka_broker_sasl_password,
            "ssl.ca.location": kafka_broker_ca_certificate,
        }

        source_api_username: str = os.getenv("SOURCE_API_USERNAME")
        source_api_password: str = os.getenv("SOURCE_API_PASSWORD")
        credentials = f"{source_api_username}:{source_api_password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        self._headers = {"Authorization": f"Basic {encoded_credentials}"}
        self._source_api_ws_url: str = os.getenv("SOURCE_API_WS_URL")

        log.info("Sensor Publisher Connector initialised")

    def _process_websocket_msg(self, msg_dict: dict):
        """It processes a web socket message and adds sensor key and sensor value to a queue.

        Args:
            msg_dict (dict): A message with sensor key and value received from the Server.
        """

        sensor_key: str = msg_dict.get("subscription", {}).get("key")
        if not sensor_key:
            log.debug("Bad format of Sensor Key %s", sensor_key)
            return

        sensor_value = msg_dict.get("data", {}).get("value")
        if sensor_value is None:
            log.debug(
                "Bad format of Sensor Value for Sensor Key '%s': %s",
                sensor_key,
                sensor_value,
            )
            return

        try:
            sensor_value = round(float(sensor_value), 3)
        except ValueError:
            log.debug(
                "Can't convert Sensor Value into float for Sensor Key '%s': %s",
                sensor_key,
                sensor_value,
            )
            return

        self._sensor_data_queue.put(
            {cnt.SENSOR_KEY: sensor_key, cnt.LAST_SHARED_VALUE: sensor_value}
        )
        log.debug(
            "Sensor Key '%s' and Sensor Value '%s' added to publish queue",
            sensor_key,
            sensor_value,
        )

    def _connect_to_websocket(self):
        """Create a web socket connection

        Returns:
            web_socket_connection (WebSocket): the websocket connection needed to receive data.
        """

        # Disable certification check
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        web_socket_connection = create_connection(
            self._source_api_ws_url,
            header=self._headers,
            sslopt={"context": ssl_context},
        )
        log.info("WebSocket connected")

        # Send the subscription message
        web_socket_connection.send(json.dumps(cnt.INITIAL_SUBSCRIPTION_PAYLOAD))
        log.info("WebSocket subscribed")

        # The first message contains the last shared value for all sensors
        subscription_response = json.loads(web_socket_connection.recv())
        log.debug("WebSocket subscription response: %s", subscription_response)

        return web_socket_connection

    def _receive_sensor_data(self):
        """Periodally wait for incoming sensor value messages from the Web Socket"""

        while True:
            try:
                log.info("Connecting to WebSocket...")
                web_socket_connection = self._connect_to_websocket()
                log.info("Waiting for incoming messages...")

                # Inner loop polls for messages
                while True:
                    try:
                        msg = web_socket_connection.recv()
                        if not (msg and isinstance(msg, str)):
                            log.warning("Received unknown message type: %s", msg)
                            continue

                        msg_dict = json.loads(msg)
                        self._process_websocket_msg(msg_dict)
                    except json.JSONDecodeError as ex:
                        log.warning(
                            "Failed to decode JSON msg %s from WebSocket message: %s",
                            msg,
                            ex,
                        )
                        continue
                    except Exception as ex:
                        log.warning("Exception while processing message: %s", ex)
                        break
            except (ConnectionError, WebSocketException) as ex:
                # For connection or client errors, reconnect
                log.warning(
                    "Reconnecting to %s in 5 seconds due to %s",
                    self._source_api_ws_url,
                    ex,
                )
                sleep(5)

    @staticmethod
    def _delivery_report(err, msg):
        """Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush()."""

        if err is not None:
            log.error("Message delivery failed: %s", err)
        else:
            log.debug("Message delivered: %s", msg.topic())

    def _process_queue(self):
        """Create an application connected to the Kafka cluster.
        Then wait for sensor messages from the internal queue,
        processes them and publish them to a Kafka topic.
        """

        log.info("Creating Kafka producer...")
        producer = Producer(self._kafka_conf)
        log.info("Kafka producer created")

        while True:
            sensor_data: dict = self._sensor_data_queue.get()
            log.debug("Received new data from queue: %s", sensor_data)

            sensor_key: str = sensor_data.get(cnt.SENSOR_KEY)
            if not sensor_key:
                log.warning("Missing sensor key in data: %s. Skipping.", sensor_data)
                continue

            cached_sensor_info: dict = self._redis_connector.get(sensor_key)
            if not cached_sensor_info:
                log.info(
                    "Sensor %s not found in cache. Missing metadata. Skipping",
                    sensor_key,
                )
                continue

            last_shared_value: float = sensor_data.get(cnt.LAST_SHARED_VALUE)
            sensor_house: str = cached_sensor_info.get(cnt.BUILDING_NAME)

            cached_sensor_info.update(
                {
                    cnt.LAST_SHARED_VALUE: last_shared_value,
                    cnt.LAST_SHARED_DATETIME: datetime.now().timestamp(),
                }
            )

            topic_name = sensor_house.lower().replace(" ", "_")

            try:
                producer.produce(
                    topic=topic_name,
                    value=json.dumps(cached_sensor_info),
                    callback=self._delivery_report,
                )
            except Exception as ex:
                log.error("Got an exception while publishing to kafka: %s", ex)
                continue

            producer.flush()
            log.debug(
                "Data published successfully to topic %s: %s",
                topic_name,
                cached_sensor_info,
            )

    def _publish_sensor_data(self):
        """Creates an iterator that iterates when exceptions are raised.
        It starts processing the internal queue and publishes data to Kafka topics.
        """

        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self._process_queue()
            except Exception as ex:
                log.error("Raised exception in publish_sensor_data %s", ex)
                log.debug(
                    "Attempting to reconnect in %ds (attempt n. %d)",
                    retry_delay,
                    attempt,
                )
                sleep(retry_delay)

    def start(self):
        """Start the publish_sensor_data thread that publishes messages to Kafka.
        Additionally starts the receive the sensor data from web socket.
        """

        Thread(target=self._publish_sensor_data, name="publish_sensor_data").start()
        self._receive_sensor_data()
