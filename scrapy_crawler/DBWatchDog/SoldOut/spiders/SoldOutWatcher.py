import json
from typing import List, Type

import scrapy
from sqlalchemy import false, null
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.Bungae.metadata import article
from scrapy_crawler.common.db import Deal, RawUsedItem, get_engine
from scrapy_crawler.common.utils.constants import BunJang, Joonggonara
from scrapy_crawler.Joonggonara.metadata.article import ArticleRoot
from scrapy_crawler.Joonggonara.TotalSearch.items import ArticleStatus


class SoldOutWatcher(scrapy.Spider):
    name = "SoldOutWatcher"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.InitCloudwatchLogger": 1,
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.UpdateLastCrawledTime": 2,
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.UpdateSoldStatus": 2,
        },
    }

    def __init__(self, n=30, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.session = sessionmaker(bind=get_engine())()

    def get_unsold_items(self) -> List[tuple[Deal, RawUsedItem]]:
        item = (
            self.session.query(Deal, RawUsedItem)
            .join(RawUsedItem, Deal.url == RawUsedItem.url)
            .filter(Deal.sold == false())
            .filter(Deal.deleted_at == null())
            .order_by(Deal.last_crawled)
            .limit(self.n)
        )

        return item.all()

    def get_article_url(self, item: Type[Deal]) -> str:
        if item.source == "중고나라":
            return Joonggonara.ARTICLE_API_URL % item.url.split("/")[-1]
        else:
            return BunJang.ARTICLE_API_URL % item.url.split("/")[-1]

    def start_requests(self):
        unsold_items = self.get_unsold_items()

        for item in unsold_items:
            deal, raw_used_item = item
            request_url = self.get_article_url(deal)
            yield scrapy.Request(
                url=request_url,
                callback=self.parse,
                errback=lambda failure: self.logger.warn(failure),
                meta={
                    "item_id": deal.id,
                    "log_id": raw_used_item.id,
                    "handle_httpstatus_list": [200, 400, 404],
                    "source": deal.source,
                },
            )

    def parse(self, response, **kwargs):
        item_id = response.meta["item_id"]
        source = response.meta["source"]
        resp_status = response.status
        log_stream_id = response.meta["log_id"]
        prod_status = "SELLING"
        price = 0

        if resp_status not in [400, 404]:
            if source == "중고나라":
                root = ArticleRoot.from_dict(json.loads(response.text))
                prod_status = (
                    root.result.saleInfo.saleStatus if root.result else "SOLD_OUT"
                )
                price = root.result.saleInfo.price if root.result else 0
            else:
                root = article.ArticleRoot.from_dict(json.loads(response.text))
                prod_status = root.data.product.saleStatus if root.data else "SOLD_OUT"
                price = root.data.product.price if root.data else 0

        yield ArticleStatus(
            id=item_id,
            log_id=log_stream_id,
            price=price,
            resp_status=resp_status,
            prod_status=prod_status,
        )
