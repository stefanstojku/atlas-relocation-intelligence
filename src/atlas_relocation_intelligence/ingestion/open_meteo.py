from typing import Any

import requests


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_min",
    "temperature_2m_max",
    "precipitation_sum",
    "sunshine_duration",
]


def fetch_daily_weather(
    latitude: float,
    longitude: float,
    timezone: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARIABLES),
    }

    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()

    if "daily" not in payload:
        raise ValueError("Open-Meteo response does not contain daily data")

    return payload


if __name__ == "__main__":
    weather = fetch_daily_weather(
        latitude=52.5200,
        longitude=13.4050,
        timezone="Europe/Berlin",
        start_date="2025-01-01",
        end_date="2025-12-31",
    )

    daily = weather["daily"]
    dates = daily["time"]

    print(f"Retrieved {len(dates)} observations for Berlin")
    print(f"Period: {dates[0]} to {dates[-1]}")
    print(f"Variables: {', '.join(daily.keys())}")