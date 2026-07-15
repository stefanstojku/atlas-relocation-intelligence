from datetime import date
from typing import Any

from sqlalchemy import text

from atlas_relocation_intelligence.database import engine
from atlas_relocation_intelligence.ingestion.open_meteo import (
    DAILY_VARIABLES,
    fetch_daily_weather,
)
from atlas_relocation_intelligence.schema import (
    create_raw_schema_and_tables,
)


def get_city(city_id: str) -> dict[str, Any]:
    statement = text(
        """
        SELECT
            city_id,
            city_name,
            latitude,
            longitude,
            timezone
        FROM raw.cities
        WHERE city_id = :city_id;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(
            statement,
            {"city_id": city_id},
        ).mappings().one()

    return dict(result)


def transform_weather(
    city_id: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    daily = payload["daily"]
    expected_fields = ["time", *DAILY_VARIABLES]

    missing_fields = [
        field for field in expected_fields if field not in daily
    ]

    if missing_fields:
        raise ValueError(
            f"Missing daily weather fields: {missing_fields}"
        )

    field_lengths = {
        field: len(daily[field]) for field in expected_fields
    }

    if len(set(field_lengths.values())) != 1:
        raise ValueError(
            f"Weather arrays have different lengths: {field_lengths}"
        )

    rows = []

    for index, observation_date in enumerate(daily["time"]):
        rows.append(
            {
                "city_id": city_id,
                "observation_date": date.fromisoformat(
                    observation_date
                ),
                "temperature_mean_c": daily[
                    "temperature_2m_mean"
                ][index],
                "temperature_min_c": daily[
                    "temperature_2m_min"
                ][index],
                "temperature_max_c": daily[
                    "temperature_2m_max"
                ][index],
                "precipitation_mm": daily[
                    "precipitation_sum"
                ][index],
                "sunshine_seconds": daily[
                    "sunshine_duration"
                ][index],
                "source": "open-meteo",
            }
        )

    return rows


def load_weather_for_city(
    city_id: str,
    start_date: str,
    end_date: str,
) -> int:
    create_raw_schema_and_tables()
    city = get_city(city_id)

    payload = fetch_daily_weather(
        latitude=float(city["latitude"]),
        longitude=float(city["longitude"]),
        timezone=city["timezone"],
        start_date=start_date,
        end_date=end_date,
    )

    rows = transform_weather(city_id, payload)

    statement = text(
        """
        INSERT INTO raw.weather_daily (
            city_id,
            observation_date,
            temperature_mean_c,
            temperature_min_c,
            temperature_max_c,
            precipitation_mm,
            sunshine_seconds,
            source
        )
        VALUES (
            :city_id,
            :observation_date,
            :temperature_mean_c,
            :temperature_min_c,
            :temperature_max_c,
            :precipitation_mm,
            :sunshine_seconds,
            :source
        )
        ON CONFLICT (city_id, observation_date) DO UPDATE SET
            temperature_mean_c = EXCLUDED.temperature_mean_c,
            temperature_min_c = EXCLUDED.temperature_min_c,
            temperature_max_c = EXCLUDED.temperature_max_c,
            precipitation_mm = EXCLUDED.precipitation_mm,
            sunshine_seconds = EXCLUDED.sunshine_seconds,
            source = EXCLUDED.source,
            loaded_at = CURRENT_TIMESTAMP;
        """
    )

    with engine.begin() as connection:
        connection.execute(statement, rows)

    return len(rows)


if __name__ == "__main__":
    row_count = load_weather_for_city(
        city_id="berlin",
        start_date="2025-01-01",
        end_date="2025-12-31",
    )

    print(f"Loaded {row_count} weather rows for Berlin")