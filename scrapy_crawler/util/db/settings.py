import logging

from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine


def get_engine():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    settings = get_project_settings()
    logging.info(
        f"Connecting to database {settings.get('DB_DATABASE')} on {settings.get('DB_HOST')}"
    )

    return create_engine(
        f"postgresql://{settings.get('DB_USER')}:"
        f"{settings.get('DB_PASSWORD')}@{settings.get('DB_HOST')}:"
        f"{settings.get('DB_PORT')}/{settings.get('DB_DATABASE')}",
        connect_args={"options": "-csearch_path=macguider"},
        echo=True,
    )
