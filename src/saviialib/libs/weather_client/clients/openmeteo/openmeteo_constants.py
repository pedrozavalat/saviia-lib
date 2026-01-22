AIR_QUALITY_API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_QUALITY_API_URL = "https://api.open-meteo.com/v1/forecast"

METRIC_MAP = {
    "air_temperature": {
        "name": "temperature_2m",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["min", "max", "mean"],
    },
    "c02": {"name": "carbon_dioxide", "source": AIR_QUALITY_API_URL},
    "global_radiation": {
        "name": "direct_normal_irradiance",
        "source": WEATHER_QUALITY_API_URL,
    },
    "humidity": {
        "name": "relative_humidity_2m",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["min", "max", "mean"],
    },
    "pico_moisture_1": {
        "name": "soil_moisture_0_to_1cm",
        "source": WEATHER_QUALITY_API_URL,
    },
    "pico_soil_temperature_1": {
        "name": "soil_temperature_0cm",
        "source": WEATHER_QUALITY_API_URL,
    },
    "precipitation": {
        "name": "precipitation",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["sum", "hours"],
    },
    "precipitation_probability": {
        "name": "precipitation_probability",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["min", "max", "mean"],
    },
    "pressure": {
        "name": "surface_pressure",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["min", "max", "mean"],
    },
    "wind_speed": {
        "name": "wind_speed_10m",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["min", "max", "mean"],
    },
    "wind_direction": {
        "name": "wind_direction_10m",
        "source": WEATHER_QUALITY_API_URL,
        "aggr": ["dominant"],
    },
}
DONT_SUPPORT_AGGR = {
    "carbon_dioxide",
    "direct_normal_irradiance",
    "soil_temperature_0cm",
    "soil_moisture_0_to_1cm",
}
