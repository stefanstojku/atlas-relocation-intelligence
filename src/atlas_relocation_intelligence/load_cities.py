import csv
from pathlib import Path

from sqlalchemy import text

from atlas_relocation_intelligence.database import engine
from atlas_relocation_intelligence.schema import create_raw_schema_and_tables


CITIES_FILE = Path(__file__).resolve().parents[2] / "data" / "cities.csv"


def load_cities() -> int:
    create_raw_schema_and_tables()

    with CITIES_FILE.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    for row in rows:
        row["latitude"] = float(row["latitude"])
        row["longitude"] = float(row["longitude"])

    statement = text(
        """
        INSERT INTO raw.cities (
            city_id,
            city_name,
            country_code,
            latitude,
            longitude,
            timezone,
            currency
        )
        VALUES (
            :city_id,
            :city_name,
            :country_code,
            :latitude,
            :longitude,
            :timezone,
            :currency
        )
        ON CONFLICT (city_id) DO UPDATE SET
            city_name = EXCLUDED.city_name,
            country_code = EXCLUDED.country_code,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            timezone = EXCLUDED.timezone,
            currency = EXCLUDED.currency,
            loaded_at = CURRENT_TIMESTAMP;
        """
    )

    with engine.begin() as connection:
        connection.execute(statement, rows)

    return len(rows)


if __name__ == "__main__":
    row_count = load_cities()
    print(f"Loaded {row_count} cities into raw.cities")