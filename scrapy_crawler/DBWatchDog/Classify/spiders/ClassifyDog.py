from typing import Type

import scrapy
from scrapy import signals
from scrapy.exceptions import DropItem
from sqlalchemy import false, null, true
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db.models import RawUsedItem
from scrapy_crawler.common.db.settings import get_engine
from scrapy_crawler.common.slack.SlackBots import LabelingSlackBot
from scrapy_crawler.common.utils.constants import CONSOLE_URL
from scrapy_crawler.DBWatchDog.items import UnClassifiedItem


class ClassifyDog(scrapy.Spider):
    name = "ClassifyDog"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.DBWatchDog.Classify.pipelines.InitCloudwatchLogger": 1,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.CategoryClassifierPipeline": 2,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.ModelClassifierPipeline": 3,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.ChipClassifierPipeline": 4,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.SystemClassifierPipeline": 5,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.ModelClassifierPipeline": 6,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.GenerationClassifierPipeline": 7,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.StorageClassifierPipeline": 8,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.CellularClassifierPipeline": 9,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.UnusedClassifierPipeline": 10,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.AppleCarePlusClassifierPipeline": 11,
            "scrapy_crawler.DBWatchDog.Classify.ipad_pipelines.IpadClassifyPipeline": 12,
            "scrapy_crawler.DBWatchDog.Classify.macbook_pipelines.MacbookClassifyPipeline": 13,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.PersistRawUsedItemPipeline": 14,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.LabelingAlertPipeline": 15,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.PersistDealPipeline": 16,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = sessionmaker(bind=get_engine())()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.item_dropped, signal=signals.item_dropped)
        return spider

    def item_dropped(self, item, response, exception: DropItem, spider):
        id = item["id"]
        self.logger.info(
            f"[{type(self).__name__}][{id}] item dropped with Error msg : {exception}"
        )
        self.session.query(RawUsedItem).filter(RawUsedItem.id == id).update(
            {
                RawUsedItem.classified: true(),
            }
        )
        self.session.commit()

        bot = LabelingSlackBot()
        bot.post_labeling_message(
            console_url=CONSOLE_URL % id,
            msg=f"{exception}",
        )

    def get_unclassified_items(self) -> list[Type[RawUsedItem]]:
        item = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.classified == false())
            .filter(RawUsedItem.type == null())
            .filter(RawUsedItem.item_id == null())
            .order_by(RawUsedItem.date)
            .limit(30)
        )
        return item.all()

    def start_requests(self):
        # Fake fetch
        yield scrapy.Request(url="https://www.google.com", callback=self.parse)

    def parse(self, response, **kwargs):
        unclassified_items = self.get_unclassified_items()

        for item in unclassified_items:
            yield UnClassifiedItem(
                id=item.id,
                title=item.title,
                content=item.content,
                price=item.price,
                url=item.url,
                source=item.source,
            )
