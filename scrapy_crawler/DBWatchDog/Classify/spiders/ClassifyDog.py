import logging
from typing import Optional, Type

import scrapy
import watchtower
from scrapy import signals
from scrapy.exceptions import DropItem
from sqlalchemy import false, null, true
from sqlalchemy.orm import sessionmaker
from twisted.python.failure import Failure

from scrapy_crawler.common.db.models import DroppedItem, RawUsedItem
from scrapy_crawler.common.db.settings import get_engine
from scrapy_crawler.common.slack.SlackBots import ExceptionSlackBot
from scrapy_crawler.common.utils.helpers import (
    exception_to_category_code,
    get_local_timestring,
)
from scrapy_crawler.DBWatchDog.items import UnClassifiedItem


class ClassifyDog(scrapy.Spider):
    name = "ClassifyDog"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.DBWatchDog.Classify.pipelines.CategoryClassifierPipeline": 1,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.ModelClassifierPipeline": 2,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.ChipClassifierPipeline": 3,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.SystemClassifierPipeline": 4,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.ModelClassifierPipeline": 5,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.GenerationClassifierPipeline": 6,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.StorageClassifierPipeline": 7,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.CellularClassifierPipeline": 8,
            "scrapy_crawler.DBWatchDog.Classify.iphone_pipelines.GenerationClassifierPipeline": 9,
            "scrapy_crawler.DBWatchDog.Classify.iphone_pipelines.ModelClassifierPipeline": 10,
            "scrapy_crawler.DBWatchDog.Classify.iphone_pipelines.StorageClassifierPipeline": 11,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.UnusedClassifierPipeline": 12,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.AppleCarePlusClassifierPipeline": 13,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.IpadClassifyPipeline": 14,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.MacbookClassifyPipeline": 15,
            "scrapy_crawler.DBWatchDog.Classify.iphone_pipelines.IphoneClassifyPipeline": 16,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.PersistRawUsedItemPipeline": 17,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.LabelingAlertPipeline": 18,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.PersistDealPipeline": 19,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.DealAlertPipeline": 20,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cw_handler: Optional[watchtower.CloudWatchLogHandler] = None
        self.session = sessionmaker(bind=get_engine())()
        self.exception_slack_bot = ExceptionSlackBot()
        self.init_cloudwatch_logger()

    def init_cloudwatch_logger(self):
        logger = logging.getLogger(self.name)

        console_handler = logging.StreamHandler()
        self.cw_handler = watchtower.CloudWatchLogHandler(
            log_group="scrapy-chatgpt",
            stream_name="",
        )

        logger.addHandler(console_handler)
        logger.addHandler(self.cw_handler)

    def close_spider(self, spider):
        self.session.close()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(spider.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(spider.item_error, signal=signals.item_error)
        return spider

    def item_error(self, item, response, spider, failure: Failure):
        self.exception_slack_bot.post_unhandled_message(
            spider.name, failure.getErrorMessage()
        )

    def item_dropped(self, item, response, exception, spider):
        if type(exception) == DropItem:
            return

        if (category_code := exception_to_category_code(exception)) is None:
            logging.error(
                f"[{type(self).__name__}] item dropped with unknown Error msg : {exception}"
            )

        id = item["id"]
        try:
            self.session.query(RawUsedItem).filter(RawUsedItem.id == id).update(
                {
                    RawUsedItem.classified: true(),
                }
            )
            self.session.commit()

            self.session.add(
                DroppedItem(
                    source=item["source"],
                    url=item["url"],
                    category=category_code,
                    dropped_at=get_local_timestring(),
                )
            )
            self.session.commit()
        except Exception:
            logging.error(
                f"[{type(self).__name__}] item dropped with unknown Error msg : {exception}"
            )
            self.session.rollback()

    def item_scraped(self, item, response, spider):
        self.cw_handler.flush()

    def get_unclassified_items(self) -> list[Type[RawUsedItem]]:
        item = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.classified == false())
            .filter(RawUsedItem.type == null())
            .filter(RawUsedItem.item_id == null())
            .filter(RawUsedItem.title != null())  # 당근마켓 메타 크롤링 데이터 제외
            .order_by(RawUsedItem.date)
            .limit(50)
        )
        return item.all()

    def start_requests(self):
        # Fake fetch
        yield scrapy.Request(url="https://www.google.com", callback=self.parse)

    def parse(self, response, **kwargs):
        unclassified_items = self.get_unclassified_items()

        for item in unclassified_items:
            self.cw_handler.log_stream_name = str(item.id)
            yield UnClassifiedItem(
                id=item.id,
                title=item.title,
                content=item.content,
                price=item.price,
                url=item.url,
                source=item.source,
            )
