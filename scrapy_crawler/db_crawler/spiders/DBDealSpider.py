import logging
from typing import Type

import scrapy
from sqlalchemy import null
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.db_crawler.items import DealItem
from scrapy_crawler.util.db.models import Deal
from scrapy_crawler.util.db.settings import get_engine


class DBDealSpider(scrapy.Spider):
    name = "DBDealSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.db_crawler.pipelines.FillDealPipeline": 1,
        },
    }

    def __init__(self):
        super().__init__()
        self.session = sessionmaker(bind=get_engine())()

    def get_null_deal_items(self) -> list[Type[Deal]]:
        try:
            item = self.session.query(Deal).filter(Deal.title == null())
            return item.all()
        except Exception as e:
            logging.error(e)
            return []

    def start_requests(self):
        # Fake fetch
        yield scrapy.Request(url="https://www.google.com", callback=self.parse)

    def parse(self, response, **kwargs):
        null_deal_items = self.get_null_deal_items()

        for item in null_deal_items:
            yield DealItem(
                id=item.id,
                type=item.type,
                item_id=item.item_id,
                price=item.price,
                sold=item.sold,
                unused=item.unused,
                source=item.source,
                url=item.url,
                image=item.image,
                date=item.date,
                last_crawled=item.last_crawled,
                writer=item.writer,
                title=item.title,
                content=item.content,
                apple_care=item.apple_care,
            )
