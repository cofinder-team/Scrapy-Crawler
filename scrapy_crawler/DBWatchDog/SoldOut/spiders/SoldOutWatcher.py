import json
import logging
from typing import List, Optional

import scrapy
import watchtower
from scrapy import Selector, signals
from sqlalchemy import false, null
from sqlalchemy.orm import sessionmaker
from twisted.python.failure import Failure

from scrapy_crawler.Bungae.metadata import article
from scrapy_crawler.common.db import Deal, RawUsedItem, get_engine
from scrapy_crawler.common.enums import DgArticleStatusEnum
from scrapy_crawler.common.enums.SourceEnum import SourceEnum
from scrapy_crawler.common.slack.SlackBots import ExceptionSlackBot
from scrapy_crawler.common.utils.constants import BunJang, Joonggonara
from scrapy_crawler.Joonggonara.metadata.article import ArticleRoot
from scrapy_crawler.Joonggonara.TotalSearch.items import ArticleStatus


class SoldOutWatcher(scrapy.Spider):
    name = "SoldOutWatcher"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.UpdateLastCrawledTime": 1,
            "scrapy_crawler.DBWatchDog.SoldOut.pipelines.UpdateSoldStatus": 2,
        },
    }

    def __init__(self, n=100, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.cw_handler: Optional[watchtower.CloudWatchLogHandler] = None
        self.exception_slack_bot: ExceptionSlackBot = ExceptionSlackBot()
        self.session = sessionmaker(bind=get_engine())()
        self.init_cloudwatch_logger()

    def item_error(self, item, response, spider, failure: Failure):
        self.exception_slack_bot.post_unhandled_message(
            spider.name, failure.getErrorMessage()
        )

    def init_cloudwatch_logger(self):
        logger = logging.getLogger(self.name)

        console_handler = logging.StreamHandler()
        self.cw_handler = watchtower.CloudWatchLogHandler(
            log_group="scrapy-chatgpt",
            stream_name="",
        )

        logger.addHandler(console_handler)
        logger.addHandler(self.cw_handler)

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

    def get_article_url(self, item: Deal) -> str:
        if item.source == SourceEnum.JOONGGONARA.value:
            return Joonggonara.ARTICLE_API_URL % item.url.split("/")[-1]
        elif item.source == SourceEnum.BUNGAE.value:
            return BunJang.ARTICLE_API_URL % item.url.split("/")[-1]
        elif item.source == SourceEnum.DAANGN.value:
            return item.url
        else:
            raise Exception(f"Unknown source: {item.source}")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_error, signal=signals.item_error)
        crawler.signals.connect(spider.flush_log, signal=signals.item_scraped)
        return spider

    def flush_log(self, item, response, spider):
        self.cw_handler.flush()

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
        price = 0

        if source == SourceEnum.DAANGN.value:
            sel: Selector = Selector(response)
            prod_status = DgArticleStatusEnum.from_response(response).value
            raw_price = sel.css(
                "#content > #article-description > #article-price::attr(content)"
            ).get()
            price = int(raw_price.split(".")[0]) if raw_price.split(".")[0] != "" else 0
        elif source == SourceEnum.BUNGAE.value:
            if resp_status == 400:
                prod_status = "SOLD_OUT"
            else:
                root = article.ArticleRoot.from_dict(json.loads(response.text))
                prod_status = root.data.product.saleStatus if root.data else "SOLD_OUT"
                price = root.data.product.price if root.data else 0
        elif source == SourceEnum.JOONGGONARA.value:
            if resp_status == 404:
                prod_status = "SOLD_OUT"
            else:
                root = ArticleRoot.from_dict(json.loads(response.text))
                prod_status = (
                    root.result.saleInfo.saleStatus if root.result else "SOLD_OUT"
                )
                price = root.result.saleInfo.price if root.result else 0
        else:
            raise Exception(f"Unknown source: {source}")

        self.cw_handler.log_stream_name = str(log_stream_id)
        yield ArticleStatus(
            id=item_id,
            price=price,
            resp_status=resp_status,
            prod_status=prod_status,
            log_id=log_stream_id,
        )
