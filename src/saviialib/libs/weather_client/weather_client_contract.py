from abc import ABC, abstractmethod
from .types.weather_client_types import ForecastArgs


class WeatherClientContract(ABC):
    @property
    @abstractmethod
    def latitude(self):
        pass

    @property
    @abstractmethod
    def longitude(self):
        pass

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def forecast(self, args: ForecastArgs) -> dict:
        """
        Fetch weather forecast data for the given metric and date range.

        Args:
            args: ForecastArgs containing:
                - query: WeatherQuery with metric (e.g., WeatherMetric.AIRTEMP) and show_aggregates flag
                - start_date: Start date string (yyyy-mm-dd)
                - end_date: End date string (yyyy-mm-dd)

        Returns:
            dict: JSON response from the weather API containing hourly (and daily if aggregates requested) data
        """
        pass

    @abstractmethod
    async def metrics(self) -> dict:
        """
        This method returns the available weather metrics supported by the client.

        Args:
            None
        Returns:
            dict: A dictionary mapping metric names to their descriptions. If the aggregation attribute
            is empty, it means the metric does not support aggregations (e.g. min, max, etc).
        """
        pass
