import pytest
from ngn.sensor.cache.sensor_cache import SensorCache

SENSOR_KEY = "sensor_key"
SENSOR_NAME = "sensor_name"
BUILDING_NAME = "building_name"
ROOM_NAME = "room_name"
FLOOR_NAME = "floor_name"
SERVICE_TYPE = "service_type"
OBJECT_NAME = "object_name"
MEASUREMENT_TYPE = "measurement_type"

SENSOR_INFO = [
    {
        "caption": "House 2_Kitchen_Electric_Hob_Current",
        "code": 0,
        "meta": {
            "description": "House 2_Floor1_Kitchen_Electric_Hob_Current",
            "format": 9,
            "keys": ["CO:3999", "CO@2_0_205"],
            "tags": ["House2", "Floor1", "Kitchen", "Electric", "Hob", "Current"],
            "maxValue": 2147483647.0,
            "minValue": -2147483648.0,
            "caption": "House 2_Kitchen_Electric_Hob_Current",
            "offset": 0,
            "grpadr": "2/0/205",
        },
        "key": "CO@2_0_205",
    },
    {
        "caption": "House 1_Kitchen_Water_SinkHot_Temp",
        "code": 0,
        "meta": {
            "description": "House 1_Floor1_Kitchen_Water_SinkHot_Temp",
            "format": 4,
            "keys": ["CO:3901", "CO@1_3_13"],
            "tags": ["House1", "Floor1", "Kitchen", "Water", "SinkHot", "Temp"],
            "maxValue": 670760.0,
            "minValue": -671088.0,
            "caption": "House 1_Kitchen_Water_SinkHot_Temp",
            "offset": 0,
            "grpadr": "1/3/13",
        },
        "key": "CO@1_3_13",
    },
    {
        "caption": "House 2_Global_Water_Meter_Flow",
        "code": 0,
        "meta": {
            "description": "House 2_Floor_Global_Water_Meter_Flow",
            "format": 9,
            "keys": ["CO:3167", "CO@2_3_1"],
            "tags": ["House2", "Floor", "Global", "Water", "Meter", "Flow"],
            "maxValue": 2147483647.0,
            "minValue": -2147483648.0,
            "caption": "House 2_Global_Water_Meter_Flow",
            "offset": 0,
            "grpadr": "2/3/1",
        },
        "key": "CO@2_3_1",
    },
    {
        "caption": "House 4_WWHRS_ShowerMIX_Temp",
        "code": 0,
        "meta": {
            "description": "House 4_WWHRS_ShowerMIX_Temp",
            "format": 4,
            "keys": ["CO:5139", "CO@4_3_148"],
            "tags": ["House4", "WWHRS", "ShowerMIX", "Temp"],
            "maxValue": 670760.0,
            "minValue": -671088.0,
            "caption": "House 4_WWHRS_ShowerMIX_Temp",
            "offset": 0,
            "grpadr": "4/3/148",
        },
        "key": "CO@4_3_148",
    },
    {
        "caption": "House 8_Weather_ExternalPrecipitation",
        "code": 0,
        "meta": {
            "description": "House 8_Floor2_Weather_ExternalPrecipitation",
            "format": 1,
            "keys": ["CO:5000", "CO@10_0_3"],
            "tags": ["House8", "Floor2", "Weather", "ExternalPrecipitation"],
            "maxValue": 1.0,
            "minValue": 0.0,
            "caption": "House 8_Weather_ExternalPrecipitation",
            "offset": 0,
            "grpadr": "10/0/3",
        },
        "key": "CO@10_0_3",
    },
]


@pytest.mark.parametrize(
    "sensor_msg, exp_sensor_key, exp_sensor_name",
    [
        (
            {
                "caption": "House 2_Kitchen_Electric_Hob_Current",
                "code": 0,
                "meta": {
                    "description": "House 2_Floor1_Kitchen_Electric_Hob_Current",
                    "format": 9,
                    "keys": ["CO:3999", "CO@2_0_205"],
                    "tags": [
                        "House2",
                        "Floor1",
                        "Kitchen",
                        "Electric",
                        "Hob",
                        "Current",
                    ],
                    "maxValue": 2147483647.0,
                    "minValue": -2147483648.0,
                    "caption": "House 2_Kitchen_Electric_Hob_Current",
                    "offset": 0,
                    "grpadr": "2/0/205",
                },
                "key": "CO@2_0_205",
            },
            "CO@2_0_205",
            "House 2_Floor1_Kitchen_Electric_Hob_Current",
        ),
        (
            {
                "caption": "House 1_Kitchen_Water_SinkHot_Temp",
                "code": 0,
                "meta": {
                    "description": "House 1_Floor1_Kitchen_Water_SinkHot_Temp",
                    "format": 4,
                    "keys": ["CO:3901", "CO@1_3_13"],
                    "tags": ["House1", "Floor1", "Kitchen", "Water", "SinkHot", "Temp"],
                    "maxValue": 670760.0,
                    "minValue": -671088.0,
                    "caption": "House 1_Kitchen_Water_SinkHot_Temp",
                    "offset": 0,
                    "grpadr": "1/3/13",
                },
                "key": "CO@1_3_13",
            },
            "CO@1_3_13",
            "House 1_Floor1_Kitchen_Water_SinkHot_Temp",
        ),
        (
            {
                "caption": "House 2_Global_Water_Meter_Flow",
                "code": 0,
                "meta": {
                    "description": "House 2_Floor_Global_Water_Meter_Flow",
                    "format": 9,
                    "keys": ["CO:3167", "CO@2_3_1"],
                    "tags": ["House2", "Floor", "Global", "Water", "Meter", "Flow"],
                    "maxValue": 2147483647.0,
                    "minValue": -2147483648.0,
                    "caption": "House 2_Global_Water_Meter_Flow",
                    "offset": 0,
                    "grpadr": "2/3/1",
                },
                "key": "CO@2_3_1",
            },
            "CO@2_3_1",
            "House 2_Floor_Global_Water_Meter_Flow",
        ),
        (
            {
                "caption": "House 4_WWHRS_ShowerMIX_Temp",
                "code": 0,
                "meta": {
                    "description": "House 4_WWHRS_ShowerMIX_Temp",
                    "format": 4,
                    "keys": ["CO:5139", "CO@4_3_148"],
                    "tags": ["House4", "WWHRS", "ShowerMIX", "Temp"],
                    "maxValue": 670760.0,
                    "minValue": -671088.0,
                    "caption": "House 4_WWHRS_ShowerMIX_Temp",
                    "offset": 0,
                    "grpadr": "4/3/148",
                },
                "key": "CO@4_3_148",
            },
            "CO@4_3_148",
            "House 4_WWHRS_ShowerMIX_Temp",
        ),
        (
            {
                "caption": "House 8_Weather_ExternalPrecipitation",
                "code": 0,
                "meta": {
                    "description": "House 8_Floor2_Weather_ExternalPrecipitation",
                    "format": 1,
                    "keys": ["CO:5000", "CO@10_0_3"],
                    "tags": ["House8", "Floor2", "Weather", "ExternalPrecipitation"],
                    "maxValue": 1.0,
                    "minValue": 0.0,
                    "caption": "House 8_Weather_ExternalPrecipitation",
                    "offset": 0,
                    "grpadr": "10/0/3",
                },
                "key": "CO@10_0_3",
            },
            "CO@10_0_3",
            "House 8_Floor2_Weather_ExternalPrecipitation",
        ),
    ],
)
def test_message_parsing(sensor_msg: dict, exp_sensor_key: str, exp_sensor_name: str):
    assert sensor_msg.get("key") == exp_sensor_key
    assert sensor_msg.get("meta", {}).get("description") == exp_sensor_name


@pytest.mark.parametrize(
    "sensor_key, sensor_name, expected_values",
    [
        (
            "CO@2_0_205",
            "House 2_Floor1_Kitchen_Electric_Hob_Current",
            {
                SENSOR_KEY: "CO@2_0_205",
                SENSOR_NAME: "House 2_Floor1_Kitchen_Electric_Hob_Current",
                BUILDING_NAME: "House 2",
                ROOM_NAME: "Kitchen",
                FLOOR_NAME: "Floor1",
                SERVICE_TYPE: "Electric",
                OBJECT_NAME: "Hob",
                MEASUREMENT_TYPE: "Current",
            },
        ),
        (
            "CO@1_3_13",
            "House 1_Floor1_Kitchen_Water_SinkHot_Temp",
            {
                SENSOR_KEY: "CO@1_3_13",
                SENSOR_NAME: "House 1_Floor1_Kitchen_Water_SinkHot_Temp",
                BUILDING_NAME: "House 1",
                ROOM_NAME: "Kitchen",
                FLOOR_NAME: "Floor1",
                SERVICE_TYPE: "Water",
                OBJECT_NAME: "SinkHot",
                MEASUREMENT_TYPE: "Temp",
            },
        ),
        (
            "CO@2_3_1",
            "House 2_Floor_Global_Water_Meter_Flow",
            {
                SENSOR_KEY: "CO@2_3_1",
                SENSOR_NAME: "House 2_Floor_Global_Water_Meter_Flow",
                BUILDING_NAME: "House 2",
                ROOM_NAME: "Global",
                FLOOR_NAME: "Floor",
                SERVICE_TYPE: "Water",
                OBJECT_NAME: "Meter",
                MEASUREMENT_TYPE: "Flow",
            },
        ),
        (
            "CO@4_3_148",
            "House 4_WWHRS_ShowerMIX_Temp",
            {
                SENSOR_KEY: "CO@4_3_148",
                SENSOR_NAME: "House 4_WWHRS_ShowerMIX_Temp",
                BUILDING_NAME: "House 4",
                ROOM_NAME: "",
                FLOOR_NAME: "",
                SERVICE_TYPE: "WWHRS",
                OBJECT_NAME: "ShowerMIX",
                MEASUREMENT_TYPE: "Temp",
            },
        ),
        (
            "CO@10_0_3",
            "House 8_Floor2_Weather_ExternalPrecipitation",
            {
                SENSOR_KEY: "CO@10_0_3",
                SENSOR_NAME: "House 8_Floor2_Weather_ExternalPrecipitation",
                BUILDING_NAME: "House 8",
                ROOM_NAME: "",
                FLOOR_NAME: "Floor2",
                SERVICE_TYPE: "ExternalPrecipitation",
                OBJECT_NAME: "",
                MEASUREMENT_TYPE: "ExternalPrecipitation",
            },
        ),
        (
            None,
            "House 8_Floor2_Weather_ExternalPrecipitation",
            None,
        ),
        (
            "CO@10_0_3",
            "Bad formatted string",
            None,
        ),
    ],
)
def test_sensor_info_parsing(sensor_key: str, sensor_name: str, expected_values: dict):
    sensor_cache = SensorCache()
    sensor_info = sensor_cache._parse_sensor_name(sensor_key, sensor_name)

    if not sensor_info:
        assert not expected_values
    else:
        assert len(sensor_info.keys()) == len(expected_values.keys())

        assert sensor_info.get(SENSOR_KEY) == expected_values.get(SENSOR_KEY)
        assert sensor_info.get(SENSOR_NAME) == expected_values.get(SENSOR_NAME)
        assert sensor_info.get(BUILDING_NAME) == expected_values.get(BUILDING_NAME)
        assert sensor_info.get(ROOM_NAME) == expected_values.get(ROOM_NAME)
        assert sensor_info.get(FLOOR_NAME) == expected_values.get(FLOOR_NAME)
        assert sensor_info.get(SERVICE_TYPE) == expected_values.get(SERVICE_TYPE)
        assert sensor_info.get(OBJECT_NAME) == expected_values.get(OBJECT_NAME)
        assert sensor_info.get(MEASUREMENT_TYPE) == expected_values.get(
            MEASUREMENT_TYPE
        )
