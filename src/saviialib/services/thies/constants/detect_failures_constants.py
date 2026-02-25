from saviialib.libs.weather_client import WeatherMetric

"""
Sensors group:
c	Pressure
c	Pressure Temperature
d	Precipitation
e	WS
e	WD
f	Humidity
f	AirTemperature
g	Radiation
h	PicoMoisture 1
h	PicoSoilTemp 1
i	PicoMoisture 2
i	PicoSoilTemp 2
j	CO2
k	UVA Radiation
k	UVB Radiation
k	PAR Radiation
"""

COLS_TO_KEEP = {
    "Date": (),
    "Time": (),
    "Pressure": ("MIN", "MAX"),
    "Precipitation": (),
    # "WS": ("MIN", "MAX gust"), # TODO: Search new API
    "WD": ("MIN", "MAX gust"),
    "Humidity": ("MIN", "MAX"),
    "Radiation": ("MIN", "MAX"),
    "PicoMoisture 1": ("MIN", "MAX"),
    "CO2": ("MIN", "MAX"),
}

# Mapping from THIES original columns to Weather Client (Open Meteo) metrics name.
METRIC_TO_WEATHER_PARAM = {
    "Pressure": WeatherMetric.PRESSURE,
    "Precipitation": WeatherMetric.PRECIPITATION,
    # "WS": WeatherMetric.WS, # TODO: Search new API
    "WD": WeatherMetric.WD,
    "Humidity": WeatherMetric.HUMIDITY,
    "Radiation": WeatherMetric.RADIATION,
    "PicoMoisture 1": WeatherMetric.PICOMOISTURE1,
    "CO2": WeatherMetric.CO2,
}

# Out of bound umbral for each day
UMBRAL = 0.75

# Sensor related for each metric.
METRICS_TO_SENSORS = {
    "Pressure": "Barometer",
    "Precipitation": "Rain gauge",
    "Humidity": "Thermo-hygrometer",
    "WS": "Anemometer",
    "WD": "Wind vane",
    "Radiation": "Pyranometer",
    "PicoMoisture 1": "Soil moisture and soil temperature sensor (PICO 1)",
    "CO2": "CO2 sensor (NDIR)",
}
