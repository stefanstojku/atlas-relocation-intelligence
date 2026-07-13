from sqlalchemy import create_engine, text

from atlas_relocation_intelligence.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)


def verify_connection() -> tuple[str, str]:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user;")
        ).one()

    return result[0], result[1]