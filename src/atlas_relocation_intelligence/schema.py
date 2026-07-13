from sqlalchemy import text

from atlas_relocation_intelligence.database import engine


def create_raw_schema_and_tables() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS raw.cities (
                    city_id VARCHAR(50) PRIMARY KEY,
                    city_name VARCHAR(100) NOT NULL,
                    country_code CHAR(2) NOT NULL,
                    latitude NUMERIC(8, 5) NOT NULL
                        CHECK (latitude BETWEEN -90 AND 90),
                    longitude NUMERIC(8, 5) NOT NULL
                        CHECK (longitude BETWEEN -180 AND 180),
                    timezone VARCHAR(50) NOT NULL,
                    currency CHAR(3) NOT NULL,
                    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
        )