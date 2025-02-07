import base64
import json
import os
import ssl
from logging import config, getLogger
from time import sleep
from typing import List

import requests
from requests.auth import HTTPBasicAuth
from websocket import WebSocketException, create_connection

# Logging Configurations
LOGGING_LEVEL = "INFO"
LOGGING_CONFIGURATION = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(asctime)s] [%(module)s] %(levelname)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOGGING_LEVEL,
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"level": LOGGING_LEVEL, "handlers": ["console"]},
}
SLEEP_TIME = 5
INITIAL_SUBSCRIPTION_PAYLOAD = {
    "type": "subscribe",
    "param": {"keys": ["CO@*"], "context": "iotics-connector-cev"},
}

config.dictConfig(LOGGING_CONFIGURATION)
log = getLogger(__name__)


def test_server_metadata():
    def get_sensor_metadata(endpoint: str) -> List[dict]:
        log.info("Calling endpoint %s...", endpoint)
        source_api_username: str = os.getenv("SOURCE_API_USERNAME")
        source_api_password: str = os.getenv("SOURCE_API_PASSWORD")
        credentials = f"{source_api_username}:{source_api_password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        headers = {"Authorization": f"Basic {encoded_credentials}"}
        endpoint_response = requests.get(endpoint, headers=headers, verify=False)
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

    sensor_info_endpoint = os.getenv("CONNECTOR_SOURCE_API_URL")

    successful = False
    for _ in range(2):
        from_param = 0

        while True:
            log.info("Getting new sensor info from server...")
            inner_url = sensor_info_endpoint + "&from=" + str(from_param)
            sensor_info_items = get_sensor_metadata(endpoint=inner_url)

            # If response is empty, we've got all sensors, and need to break the loop
            if not sensor_info_items:
                log.info("No more sensor info items")
                break

            for sensor_info in sensor_info_items:
                log.info("Received sensor info: %s", sensor_info)
                successful = True

            from_param += 1000

        log.info("Cache updated. Next iteration in %ds", SLEEP_TIME)
        sleep(SLEEP_TIME)

    return successful


def test_server_data():
    def process_websocket_msg(msg_dict: dict):
        log.info("Received message %s", msg_dict)

        sensor_key: str = msg_dict.get("subscription", {}).get("key")
        sensor_value = msg_dict.get("data", {}).get("value")

        if not (sensor_key and sensor_value):
            log.info(
                "Bad format of Sensor Key '%s' and/or Sensor Value '%s'",
                sensor_key,
                sensor_value,
            )

            return False

        return True

    source_api_username: str = os.getenv("SOURCE_API_USERNAME")
    source_api_password: str = os.getenv("SOURCE_API_PASSWORD")
    source_api_ws_url: str = os.getenv("SOURCE_API_WS_URL")

    auth = HTTPBasicAuth(source_api_username, source_api_password)

    successful = False
    for _ in range(3):
        if successful:
            break

        try:
            log.info("Connecting to WebSocket...")
            credentials = f"{source_api_username}:{source_api_password}"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
                "utf-8"
            )
            headers = {"Authorization": f"Basic {encoded_credentials}"}

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False  # Disable hostname verification
            ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate verification

            ws = create_connection(
                source_api_ws_url,
                header=headers,
                sslopt={"context": ssl_context},
            )
            log.info("WebSocket connected")

            # Send the subscription message
            ws.send(json.dumps(INITIAL_SUBSCRIPTION_PAYLOAD))
            log.info("WebSocket subscribed")

            # The first message contains the last shared value for all sensors
            subscription_response = json.loads(ws.recv())
            log.info("WebSocket subscription response: %s", subscription_response)

            log.info("Waiting for incoming messages...")
            counter = 0
            # Inner loop polls for messages
            for _ in range(10):
                try:
                    msg = ws.recv()
                    if not (msg and isinstance(msg, str)):
                        log.warning("Received unknown message type: %s", msg)
                        continue

                    msg_dict = json.loads(msg)
                    successful = process_websocket_msg(msg_dict)

                    if successful:
                        counter += 1

                    if counter > 10:
                        return True
                except json.JSONDecodeError as ex:
                    log.warning("Failed to decode JSON from WebSocket message: %s", ex)
                    continue
                except Exception as ex:
                    log.warning("Exception while processing message: %s", ex)
                    break
        except (ConnectionError, WebSocketException) as ex:
            # For connection or client errors, reconnect
            log.warning(
                "Reconnecting to %s in 5 seconds due to %s", source_api_ws_url, ex
            )
            sleep(5)

    return False


def main():
    log.info("Starting test_server_metadata...")
    meta_successful = test_server_metadata()
    if meta_successful:
        log.info("TEST SERVER METADATA SUCCESSFUL !!!")

    log.info("Starting test_server_data...")
    data_successful = test_server_data()
    if data_successful:
        log.info("TEST SERVER DATA SUCCESSFUL !!!")

    log.info("Test completed")


if __name__ == "__main__":
    main()
