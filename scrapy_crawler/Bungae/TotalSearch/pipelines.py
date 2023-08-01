import logging

from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.Bungae.utils.constants import ARTICLE_URL
from scrapy_crawler.common.db import RawUsedItem, get_engine
from scrapy_crawler.common.utils.helpers import (
    has_forbidden_keyword,
    save_image_from_url,
    too_low_price,
)


class DuplicateFilterPipeline:
    name = "DuplicateFilterPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        logging.warning(f"[{type(self).__name__}] start process_item {item['pid']}")
        try:
            entity = (
                self.session.query(RawUsedItem)
                .filter(RawUsedItem.url == ARTICLE_URL % str(item["pid"]))
                .first()
            )

            if entity is not None:
                raise DropItem(f"Duplicate item found: {item['pid']}")
            else:
                return item
        except Exception as e:
            logging.error(f"[{type(self).__name__}] {e}")
            raise DropItem(f"Unknown Error: {item['pid']}")


class ManualFilterPipeline:
    name = "ManualFilterPipeline"

    def process_item(self, item, spider):
        logging.warning(f"[{type(self).__name__}] start process_item {item['pid']}")

        if has_forbidden_keyword(item["title"] + item["content"]):
            raise DropItem(f"Has forbidden keyword: {item['pid']}")

        if too_low_price(item["price"]):
            raise DropItem(f"Too low price: {item['pid']}")

        return item


class PostgresExportPipeline:
    name = "PostgresExportPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        try:
            self.session.add(
                RawUsedItem(
                    writer=item["writer"],
                    title=item["title"],
                    content=item["content"],
                    price=item["price"],
                    date=item["date"],
                    source=item["source"],
                    url=ARTICLE_URL % str(item["pid"]),
                    img_url=item["img_url"],
                    image=save_image_from_url(item["img_url"]).getvalue(),
                    raw_json=item["raw_json"],
                )
            )

            self.session.commit()
            logging.warning(f"[{type(self).__name__}] {item['pid']} is saved")
        except Exception as e:
            logging.error(f"[{type(self).__name__}] {e}")
            self.session.rollback()
            raise DropItem(f"Unknown Error: {item['pid']}")

        return item
