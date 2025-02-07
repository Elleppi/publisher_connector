from datetime import datetime

import pytest
from ngn.sensor.publisher.sensor_publisher import SensorPublisher

SENSOR_KEY = "sensor_key"
LAST_SHARED_VALUE = "last_shared_value"
SENSOR_NAME = "sensor_name"
BUILDING_NAME = "building_name"
ROOM_NAME = "room_name"
FLOOR_NAME = "floor_name"
SERVICE_TYPE = "service_type"
OBJECT_NAME = "object_name"
MEASUREMENT_TYPE = "measurement_type"
LAST_SHARED_DATETIME = "last_shared_datetime"


@pytest.mark.parametrize(
    "msg_dict, exp_value",
    [
        (
            {
                "data": {"value": 34.62},
                "code": 0,
                "type": "push",
                "subscription": {"key": "CO@9_4_81"},
            },
            {SENSOR_KEY: "CO@9_4_81", LAST_SHARED_VALUE: 34.62},
        ),
        (
            {
                "data": {"value": 5156.080078125},
                "code": 0,
                "type": "push",
                "subscription": {"key": "CO@1_0_4"},
            },
            {SENSOR_KEY: "CO@1_0_4", LAST_SHARED_VALUE: 5156.08},
        ),
        (
            {
                "data": {"value": 0.0},
                "code": 0,
                "type": "push",
                "subscription": {"key": "CO@4_5_19"},
            },
            {SENSOR_KEY: "CO@4_5_19", LAST_SHARED_VALUE: 0.0},
        ),
        (
            {
                "data": {"value": 1.0},
                "code": 0,
                "type": "push",
                "subscription": {"key": "CO@1_4_123"},
            },
            {SENSOR_KEY: "CO@1_4_123", LAST_SHARED_VALUE: 1.0},
        ),
        (
            {
                "data": {"value": None},
                "code": 0,
                "type": "push",
                "subscription": {"key": None},
            },
            None,
        ),
    ],
)
def test_process_websocket_msg(msg_dict: dict, exp_value: dict):
    sensor_publisher = SensorPublisher()
    sensor_publisher._process_websocket_msg(msg_dict)

    if exp_value:
        assert not sensor_publisher._sensor_data_queue.empty()

        sensor_data = sensor_publisher._sensor_data_queue.get(block=False)

        assert sensor_data.get(SENSOR_KEY) == exp_value.get(SENSOR_KEY)
        assert sensor_data.get(LAST_SHARED_VALUE) == exp_value.get(LAST_SHARED_VALUE)


@pytest.mark.parametrize(
    "sensor_data, cached_sensor_info, exp_topic_name, exp_cached_sensor_info",
    [
        (
            {SENSOR_KEY: "CO@9_4_81", LAST_SHARED_VALUE: 34.62},
            {
                SENSOR_KEY: "CO@9_4_81",
                SENSOR_NAME: "House 9_Floor2_Bed1_Other_Humidity",
                BUILDING_NAME: "House 9",
                ROOM_NAME: "Bed1",
                FLOOR_NAME: "Floor2",
                SERVICE_TYPE: "Other",
                OBJECT_NAME: "",
                MEASUREMENT_TYPE: "Humidity",
            },
            "house_9",
            {
                SENSOR_KEY: "CO@9_4_81",
                SENSOR_NAME: "House 9_Floor2_Bed1_Other_Humidity",
                BUILDING_NAME: "House 9",
                ROOM_NAME: "Bed1",
                FLOOR_NAME: "Floor2",
                SERVICE_TYPE: "Other",
                OBJECT_NAME: "",
                MEASUREMENT_TYPE: "Humidity",
                LAST_SHARED_VALUE: 34.62,
                LAST_SHARED_DATETIME: datetime.now().timestamp(),
            },
        ),
        (
            {SENSOR_KEY: "CO@1_0_4", LAST_SHARED_VALUE: 5156.08},
            {
                SENSOR_KEY: "CO@1_0_4",
                SENSOR_NAME: "House 1_Floor_Global_Electric_AppPower",
                BUILDING_NAME: "House 1",
                ROOM_NAME: "Global",
                FLOOR_NAME: "Floor",
                SERVICE_TYPE: "Electric",
                OBJECT_NAME: "",
                MEASUREMENT_TYPE: "AppPower",
            },
            "house_1",
            {
                SENSOR_KEY: "CO@1_0_4",
                SENSOR_NAME: "House 1_Floor_Global_Electric_AppPower",
                BUILDING_NAME: "House 1",
                ROOM_NAME: "Global",
                FLOOR_NAME: "Floor",
                SERVICE_TYPE: "Electric",
                OBJECT_NAME: "",
                MEASUREMENT_TYPE: "AppPower",
                LAST_SHARED_VALUE: 5156.08,
                LAST_SHARED_DATETIME: datetime.now().timestamp(),
            },
        ),
        (
            {SENSOR_KEY: "CO@4_5_19", LAST_SHARED_VALUE: None},
            {
                SENSOR_KEY: "test",
                SENSOR_NAME: "test",
                BUILDING_NAME: "test",
                ROOM_NAME: "test",
                FLOOR_NAME: "test",
                SERVICE_TYPE: "test",
                OBJECT_NAME: "test",
                MEASUREMENT_TYPE: "test",
            },
            None,
            None,
        ),
        (
            {SENSOR_KEY: None, LAST_SHARED_VALUE: 13.0},
            {
                SENSOR_KEY: "test",
                SENSOR_NAME: "test",
                BUILDING_NAME: "test",
                ROOM_NAME: "test",
                FLOOR_NAME: "test",
                SERVICE_TYPE: "test",
                OBJECT_NAME: "test",
                MEASUREMENT_TYPE: "test",
            },
            None,
            None,
        ),
    ],
)
def test_process_queue_message(
    sensor_data: dict,
    cached_sensor_info: dict,
    exp_topic_name: str,
    exp_cached_sensor_info: dict,
):
    sensor_publisher = SensorPublisher()
    topic_name, cached_sensor_info = sensor_publisher._process_queue_message(
        sensor_data, cached_sensor_info
    )

    print(cached_sensor_info)
    print(exp_cached_sensor_info)

    if exp_cached_sensor_info:
        assert topic_name == exp_topic_name
        assert cached_sensor_info.get(LAST_SHARED_VALUE)
        assert cached_sensor_info.get(LAST_SHARED_DATETIME)
