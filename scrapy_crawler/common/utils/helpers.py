import json
import logging
from datetime import datetime, timedelta
from io import BytesIO

import requests
import watchtower
from botocore.exceptions import ClientError
from scrapy.exceptions import DropItem

from scrapy_crawler.common.enums.DroppedCategoryEnum import DroppedCategoryEnum
from scrapy_crawler.common.enums.TypeEnum import TypeEnum
from scrapy_crawler.common.utils.constants import FAKE_HEADER
from scrapy_crawler.common.utils.custom_exceptions import (
    DropAndMarkItem,
    DropDuplicateItem,
    DropForbiddenKeywordItem,
    DropTooLongTextItem,
    DropTooLowPriceItem,
    DropUnsupportedCategoryItem,
    DropUnsupportedIpadItem,
    DropUnsupportedIphoneItem,
    DropUnsupportedMacbookItem,
)
from scrapy_crawler.DBWatchDog.items import IpadItem, IphoneItem, MacbookItem


def get_local_timestring(days: int = 0) -> str:
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp() -> int:
    return int(datetime.now().timestamp() * 1000)


def to_local_timestring(timestamp: int) -> str:
    return (datetime.fromtimestamp(timestamp) + timedelta(hours=9)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def save_image_from_url(image_url) -> BytesIO:
    response = requests.get(image_url, headers=FAKE_HEADER, timeout=5)
    response.raise_for_status()

    return BytesIO(response.content)


def has_forbidden_keyword(text: str) -> bool:
    forbidden_words = [
        "매입",
        "삽니다",
        "파트너",
        "할인",
        "행사",
        "[구매]",
        "구매합니다",
        "예정",
        "최저가",
        "고객",
        "정식업체",
        "이동통신단말",
    ]

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


def too_long_text(text: str) -> bool:
    return len(text) > 4000


def item_to_type(item: IpadItem | IphoneItem | MacbookItem) -> TypeEnum:
    if type(item) == IpadItem:
        return TypeEnum.IPAD
    elif type(item) == IphoneItem:
        return TypeEnum.IPHONE
    elif type(item) == MacbookItem:
        return TypeEnum.MACBOOK
    else:
        raise ValueError(f"Unknown item type: {type(item)}")


def exception_to_category_code(exception):
    if type(exception) == DropDuplicateItem:
        category_code = DroppedCategoryEnum.Duplicate.value
    elif type(exception) == DropForbiddenKeywordItem:
        category_code = DroppedCategoryEnum.ForbiddenKeyword.value
    elif type(exception) == DropTooLongTextItem:
        category_code = DroppedCategoryEnum.LongText.value
    elif type(exception) == DropTooLowPriceItem:
        category_code = DroppedCategoryEnum.LowPrice.value
    elif type(exception) == DropUnsupportedCategoryItem:
        category_code = DroppedCategoryEnum.UnsupportedCategory.value
    elif type(exception) == DropUnsupportedIpadItem:
        category_code = DroppedCategoryEnum.UnsupportedIpad.value
    elif type(exception) == DropUnsupportedIphoneItem:
        category_code = DroppedCategoryEnum.UnsupportedIphone.value
    elif type(exception) == DropUnsupportedMacbookItem:
        category_code = DroppedCategoryEnum.UnsupportedMacbook.value
    elif type(exception) == DropItem or type(exception) == DropAndMarkItem:
        category_code = DroppedCategoryEnum.Unknown.value
    else:
        return None

    return category_code


def publish_sqs_message(queue, message_body: dict):
    try:
        response = queue.send_message(
            MessageBody=json.dumps(message_body), MessageGroupId=message_body["url"]
        )

    except ClientError as error:
        logging.error(error)
        raise error
    else:
        return response
