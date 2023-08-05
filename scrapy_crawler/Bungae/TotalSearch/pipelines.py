from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import RawUsedItem, get_engine
from scrapy_crawler.common.utils.constants import BunJang
from scrapy_crawler.common.utils.helpers import (
    has_forbidden_keyword,
    save_image_from_url,
    too_long_text,
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
        spider.logger.info(f"[{type(self).__name__}][{item['pid']}] start process_item")
        entity = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.url == BunJang.ARTICLE_URL % str(item["pid"]))
            .first()
        )

        if entity is not None:
            spider.logger.info(
                f"[{type(self).__name__}][{item['pid']}] Duplicate item found"
            )
            raise DropItem(f"Duplicate item found: {item['pid']}")
        else:
            return item


class ManualFilterPipeline:
    name = "ManualFilterPipeline"

    def process_item(self, item, spider):
        spider.logger.info(f"[{type(self).__name__}][{item['pid']}] start process_item")

        if has_forbidden_keyword(item["title"] + item["content"]):
            spider.logger.info(
                f"[{type(self).__name__}][{item['pid']}] Has forbidden keyword"
            )
            raise DropItem(f"Has forbidden keyword: {item['pid']}")

        if too_low_price(item["price"]):
            spider.logger.info(f"[{type(self).__name__}][{item['pid']}] Too low price")
            raise DropItem(f"Too low price: {item['pid']}")

        if too_long_text(item["content"]):
            spider.logger.info(f"[{type(self).__name__}][{item['pid']}] Too long text")
            raise DropItem(f"Too long text: {item['pid']}")

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
        spider.logger.info(f"[{type(self).__name__}] start process_item {item['pid']}")
        try:
            self.session.add(
                RawUsedItem(
                    writer=item["writer"],
                    title=item["title"],
                    content=item["content"],
                    price=item["price"],
                    date=item["date"],
                    source=item["source"],
                    url=BunJang.ARTICLE_URL % str(item["pid"]),
                    img_url=item["img_url"],
                    image=save_image_from_url(item["img_url"]).getvalue(),
                    raw_json=item["raw_json"],
                )
            )

            self.session.commit()
            spider.logger.info(f"[{type(self).__name__}] {item['pid']} is saved")
        except Exception as e:
            spider.logger.error(f"[{type(self).__name__}] Exception : {e}")
            self.session.rollback()
            raise DropItem(f"Unknown Error: {item['pid']}")

        return item
