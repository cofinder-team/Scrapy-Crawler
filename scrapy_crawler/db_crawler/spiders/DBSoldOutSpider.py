import json
from typing import Type

import scrapy
from sqlalchemy import false
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.db_crawler.items import JgArticle
from scrapy_crawler.util.db.models import Deal
from scrapy_crawler.util.db.settings import get_engine


class DBSoldOutSpider(scrapy.Spider):
    name = "DBSoldOutSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.db_crawler.pipelines.DBUpdateLastCrawledPipeline": 1,
            "scrapy_crawler.db_crawler.pipelines.SoldOutClassifierPipeline": 2,
            "scrapy_crawler.db_crawler.pipelines.SlackAlertPipeline": 3,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = sessionmaker(bind=get_engine())()

    def get_unsold_items(self) -> list[Type[Deal]]:
        item = (
            self.session.query(Deal)
            .filter(Deal.sold == false())
            .order_by(Deal.last_crawled)
        )
        return item.all()

    def start_requests(self):
        unsold_items = self.get_unsold_items()

        for item in unsold_items:
            id = item.id
            url = item.url.split("/")[-1]
            yield scrapy.Request(
                url=f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/10050146/articles/{url}",
                callback=self.parse,
                meta={"item_id": id},
            )

    def parse(self, response, **kwargs):
        # 글이 삭제된 경우
        if response.status == 404:
            yield JgArticle(id=response.meta["item_id"], price=0, status="SOLD_OUT")

        item_id = response.meta["item_id"]
        saleInfo = json.loads(response.text)["result"]["saleInfo"]

        price = saleInfo["price"]
        status = saleInfo["saleStatus"]

        yield JgArticle(id=item_id, price=price, status=status)
