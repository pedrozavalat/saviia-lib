"""
Constants for get_camera_rates use case.
Variables defined here are used to determine camera capture and recording rates
based on weather conditions such as precipitation and precipitation probability.
- PPb: Precipitation Probability
- P: Precipitation

Observations:
- The capture and recording rates are categorized into three states: A, B, and C.
- The value of the capture and recording times are defined in minutes.
"""

CAPTURE_TIMES = {
    "A": {"photo": 720, "video": 720},
    "B": {"photo": 30, "video": 180},
    "C": {"photo": 5, "video": 60},
}

PRECIPITATION_MATRIX = [
    # PPb_min, PPb_max, P_min, P_max, status
    # Precipitation probability [0, 30[
    (0, 30, 0, 2, "A"),
    (0, 30, 2, 5, "A"),
    (0, 30, 5, 10, "B"),
    (0, 30, 10, 20, "B"),
    (0, 30, 20, float("inf"), "B"),
    # Precipitation probability [30, 60[
    (30, 60, 0, 2, "A"),
    (30, 60, 2, 5, "B"),
    (30, 60, 5, 10, "B"),
    (30, 60, 10, 20, "C"),
    (30, 60, 20, float("inf"), "C"),
    # Precipitation probability [60, 90[
    (60, 90, 0, 2, "B"),
    (60, 90, 2, 5, "B"),
    (60, 90, 5, 10, "C"),
    (60, 90, 10, 20, "C"),
    (60, 90, 20, float("inf"), "C"),
    # Precipitation probability [90, 100]
    (90, 100, 0, 2, "B"),
    (90, 100, 2, 5, "C"),
    (90, 100, 5, 10, "C"),
    (90, 100, 10, 20, "C"),
    (90, 100, 20, float("inf"), "C"),
]
