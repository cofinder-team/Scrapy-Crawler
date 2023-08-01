import datetime
from datetime import timedelta

import scrapy
from sqlalchemy import false, null
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db.models import RawUsedItem
from scrapy_crawler.common.db.settings import get_engine
from scrapy_crawler.DBWatchDog.items import UnClassifiedItem


class ClassifyDog(scrapy.Spider):
    name = "ClassifyDog"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.DBWatchDog.Classify.pipelines.MarkAsClassifiedPipeline": 1,
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
            "scrapy_crawler.DBWatchDog.Classify.pipelines.HotDealClassifierPipeline": 14,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.LabelingAlertPipeline": 15,
            "scrapy_crawler.DBWatchDog.Classify.pipelines.PersistPipeline": 16,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = sessionmaker(bind=get_engine())()

    def get_unclassified_items(self) -> list[UnClassifiedItem]:
        item = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.classified == false())
            .filter(RawUsedItem.type == null())
            .filter(RawUsedItem.item_id == null())
            .filter(
                RawUsedItem.date
                >= f"{(datetime.datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')}"
            )
            .order_by(RawUsedItem.date)
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
