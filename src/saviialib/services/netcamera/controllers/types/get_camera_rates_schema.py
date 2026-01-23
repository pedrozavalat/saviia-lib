GET_CAMERA_RATES_SCHEMA = {
    "title": "Controller input schema for getting camera rates",
    "description": "Schema for validating input data when getting camera rates from a net camera",
    "type": "object",
    "properties": {
        "latitude": {"type": "number", "minimum": -90, "maximum": 90},
        "longitude": {"type": "number", "minimum": -180, "maximum": 180},
    },
    "required": ["latitude", "longitude"],
    "additionalProperties": False,
}
