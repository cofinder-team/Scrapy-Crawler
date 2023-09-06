from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from scrapy_crawler.Bungae.TotalSearch.spiders.BgKeywordSpider import BgKeywordSpider
from scrapy_crawler.common.db import RawUsedItem
from scrapy_crawler.common.utils.constants import BunJang
from scrapy_crawler.common.utils.custom_exceptions import (
    DropDuplicateItem,
    DropForbiddenKeywordItem,
    DropTooLongTextItem,
    DropTooLowPriceItem,
)
from scrapy_crawler.common.utils.helpers import (
    has_forbidden_keyword,
    publish_sqs_message,
    save_image_from_url,
    too_long_text,
    too_low_price,
)


class DuplicateFilterPipeline:
    name = "DuplicateFilterPipeline"

    def __init__(self):
        self.session = None

    def has_duplicate(self, item):
        return (
            self.session.query(RawUsedItem)
            .filter(
                RawUsedItem.url == BunJang.ARTICLE_URL % str(item["pid"])
                or RawUsedItem.title == item["title"]
            )
            .first()
            is not None
        )

    def process_item(self, item, spider: BgKeywordSpider):
        self.session = spider.session
        spider.logger.info(f"[{type(self).__name__}][{item['pid']}] start process_item")

        if self.has_duplicate(item):
            raise DropDuplicateItem(f"Duplicate item found: {item['pid']}")

        return item


class ManualFilterPipeline:
    name = "ManualFilterPipeline"

    def process_item(self, item, spider):
        spider.logger.info(f"[{type(self).__name__}][{item['pid']}] start process_item")

        if has_forbidden_keyword(item["title"] + item["content"]):
            raise DropForbiddenKeywordItem(f"Has forbidden keyword: {item['pid']}")

        if too_low_price(item["price"]):
            raise DropTooLowPriceItem(f"Too low price: {item['pid']}")

        if too_long_text(item["content"]):
            raise DropTooLongTextItem(f"Too long text: {item['pid']}")

        return item


class PublishSQSPipeline:
    name = "PublishSQSPipeline"

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(f"[{type(self).__name__}][{item['pid']}] start process_item")

        payload = {
            "writer": adapter["writer"],
            "title": adapter["title"],
            "content": adapter["content"],
            "price": adapter["price"],
            "date": adapter["date"],
            "url": BunJang.ARTICLE_URL % str(adapter["pid"]),
            "img_url": adapter["img_url"],
            "source": adapter["source"],
        }

        publish_sqs_message(spider.live_queue, payload)

        return item


class PostgresExportPipeline:
    name = "PostgresExportPipeline"

    def __init__(self):
        self.session = None

    def process_item(self, item, spider: BgKeywordSpider):
        self.session = spider.session
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
