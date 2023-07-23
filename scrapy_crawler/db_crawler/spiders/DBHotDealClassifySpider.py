import datetime

import scrapy
from sqlalchemy import false
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.db_crawler.items import DBItem
from scrapy_crawler.util.db.models import RawUsedItem
from scrapy_crawler.util.db.settings import get_engine


class DBHotDealClassifySpider(scrapy.Spider):
    name = "DBHotDealClassifySpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.db_crawler.pipelines.CategoryClassifierPipeline": 1,
            "scrapy_crawler.db_crawler.pipelines.MacbookModelClassifierPipeline": 2,
            "scrapy_crawler.db_crawler.pipelines.ChipClassifierPipeline": 3,
            "scrapy_crawler.db_crawler.pipelines.MacbookRamSSDClassifierPipeline": 4,
            "scrapy_crawler.db_crawler.pipelines.IpadModelClassifierPipeline": 5,
            "scrapy_crawler.db_crawler.pipelines.IpadGenerationClassifierPipeline": 6,
            "scrapy_crawler.db_crawler.pipelines.IpadStorageClassifierPipeline": 7,
            "scrapy_crawler.db_crawler.pipelines.IpadCellularClassifierPipeline": 8,
            "scrapy_crawler.db_crawler.pipelines.UnusedClassifierPipeline": 9,
            "scrapy_crawler.db_crawler.pipelines.AppleCarePlusClassifierPipeline": 10,
            "scrapy_crawler.db_crawler.pipelines.DBItemClassifierPipeline": 11,
            "scrapy_crawler.db_crawler.pipelines.HotDealClassifierPipeline": 12,
            "scrapy_crawler.db_crawler.pipelines.DBExportPipeline": 13,
            "scrapy_crawler.db_crawler.pipelines.SlackAlertPipeline": 14,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = sessionmaker(bind=get_engine())()

    def get_unclassified_items(self) -> list[DBItem]:
        from sqlalchemy import null

        item = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.classified == false())
            .filter(RawUsedItem.type == null())
            .filter(RawUsedItem.item_id == null())
            .filter(
                RawUsedItem.date
                >= f"{datetime.datetime.utcnow().date() - datetime.timedelta(days=4)}}}"
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
            yield DBItem(
                id=item.id,
                writer=item.writer,
                title=item.title,
                content=item.content,
                price=item.price,
                source=item.source,
                date=item.date,
                url=item.url,
                img_url=item.img_url,
                type=item.type,
                item_id=item.item_id,
            )
