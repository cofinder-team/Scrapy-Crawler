import logging
from datetime import datetime, timedelta
from io import BytesIO

import requests
import watchtower


def get_local_timestring() -> str:
    return (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp() -> int:
    return int(datetime.now().timestamp() * 1000)


def to_local_timestring(timestamp: int) -> str:
    return (datetime.fromtimestamp(timestamp) + timedelta(hours=9)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def save_image_from_url(image_url) -> BytesIO:
    response = requests.get(image_url, timeout=5)
    response.raise_for_status()

    return BytesIO(response.content)


def has_forbidden_keyword(text: str) -> bool:
    forbidden_words = ["매입", "삽니다", "파트너"]

    for word in forbidden_words:
        if word in text:
            return True

    return False


def too_low_price(price: int) -> bool:
    return price <= 300000


def init_cloudwatch_logger(name: str):
    console_handler = logging.StreamHandler()
    cw_handler = watchtower.CloudWatchLogHandler(
        log_group=f"scrapy-{name}",
        stream_name=f"{get_local_timestring().replace(':', '-')}",
    )

    logger = logging.getLogger(name)
    logger.addHandler(console_handler)
    logger.addHandler(cw_handler)
