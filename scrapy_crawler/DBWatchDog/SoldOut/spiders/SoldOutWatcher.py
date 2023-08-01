import json
from typing import Type

import scrapy
from sqlalchemy import false, null
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import Deal, get_engine
from scrapy_crawler.Joonggonara.metadata.article import ArticleRoot
from scrapy_crawler.Joonggonara.TotalSearch.items import ArticleStatus
from scrapy_crawler.Joonggonara.utils.constants import ARTICLE_API_URL


class SoldOutWatcher(scrapy.Spider):
    name = "SoldOutWatcher"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.UpdateLastCrawledTime": 1,
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.UpdateSoldStatus": 2,
        },
    }

    def __init__(self, n=30, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.session = sessionmaker(bind=get_engine())()

    def get_unsold_items(self) -> list[Type[Deal]]:
        item = (
            self.session.query(Deal)
            .filter(Deal.sold == false())
            .filter(Deal.deleted_at == null())
            .order_by(Deal.last_crawled)
            .limit(self.n)
        )
        return item.all()

    def start_requests(self):
        unsold_items = self.get_unsold_items()

        for item in unsold_items:
            id = item.id
            url = item.url.split("/")[-1]
            request_url = ARTICLE_API_URL % url
            yield scrapy.Request(
                url=request_url,
                callback=self.parse,
                errback=lambda failure: self.logger.warn(failure),
                meta={"item_id": id, "handle_httpstatus_list": [200, 404]},
            )

    def parse(self, response, **kwargs):
        root = ArticleRoot.from_dict(json.loads(response.text))
        id = response.meta["item_id"]
        resp_status = response.status
        prod_status = root.result.saleInfo.saleStatus if root.result else None
        price = root.result.saleInfo.price if root.result else 0

        yield ArticleStatus(
            id=id, price=price, resp_status=resp_status, prod_status=prod_status
        )
