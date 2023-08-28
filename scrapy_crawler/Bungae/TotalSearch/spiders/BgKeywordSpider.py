import json
from typing import List
from urllib import parse

import scrapy
from scrapy import signals
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.Bungae.metadata.article import ArticleRoot
from scrapy_crawler.Bungae.metadata.total_search import BgList, TotalSearchRoot
from scrapy_crawler.Bungae.TotalSearch.items import ArticleItem
from scrapy_crawler.common.db import get_engine
from scrapy_crawler.common.db.models import DroppedItem, RawUsedItem
from scrapy_crawler.common.enums import SourceEnum
from scrapy_crawler.common.utils.constants import BunJang
from scrapy_crawler.common.utils.helpers import (
    exception_to_category_code,
    get_local_timestring,
    init_cloudwatch_logger,
)


class BgKeywordSpider(scrapy.Spider):
    name = "BgKeywordSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Bungae.TotalSearch.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.PostgresExportPipeline": 3,
        }
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_cloudwatch_logger(self.name)
        self.session = sessionmaker(bind=get_engine())()
        self.keyword = keyword

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.item_dropped, signal=signals.item_dropped)
        return spider

    def item_already_dropped(self, url) -> bool:
        return (
            self.session.query(DroppedItem)
            .filter(DroppedItem.source == SourceEnum.BUNGAE.value)
            .filter(DroppedItem.url == url)
            .first()
            is not None
        )

    def item_already_crawled(self, url) -> bool:
        return (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.url == url)
            .filter(RawUsedItem.source == SourceEnum.BUNGAE.value)
            .first()
            is not None
        )

    def item_dropped(self, item, response, exception, spider):
        if self.item_already_dropped(BunJang.ARTICLE_URL % str(item["pid"])) or (
            (category_code := exception_to_category_code(exception)) is None
        ):
            return

        self.logger.info(f"Item dropped: {exception.__class__.__name__}")

        try:
            self.session.add(
                DroppedItem(
                    source=SourceEnum.BUNGAE.value,
                    category=category_code,
                    url=BunJang.ARTICLE_URL % str(item["pid"]),
                    dropped_at=get_local_timestring(),
                )
            )

            self.session.commit()
        except Exception as e:
            self.logger.error(e)
            self.session.rollback()

    def start_requests(self):
        self.logger.info(f"Start crawling keyword: {self.keyword}")
        yield scrapy.Request(
            BunJang.TOTAL_SEARCH_API_URL % parse.quote(self.keyword), self.parse
        )

    def parse(self, response):
        root = TotalSearchRoot.from_dict(json.loads(response.text))
        articles: List[BgList] = root.list

        for article in articles:
            article_url = BunJang.ARTICLE_URL % article.pid
            if self.item_already_crawled(article_url) or self.item_already_dropped(
                article_url
            ):
                continue

            yield scrapy.Request(
                BunJang.ARTICLE_API_URL % article.pid,
                callback=self.parse_article,
            )

    def parse_article(self, response):
        root = ArticleRoot.from_dict(json.loads(response.text))
        keyword = root.data.product.keywords
        content = root.data.product.description + "\n" + ", ".join(keyword)
        yield ArticleItem(
            pid=root.data.product.pid,
            title=root.data.product.name,
            content=content,
            price=root.data.product.price,
            img_url=root.data.product.imageUrl.replace("{cnt}", "1").replace(
                "{res}", "300"
            ),
            prod_status=root.data.product.status,
            date=root.data.product.updatedAt,
            raw_json=json.loads(response.text),
            source=SourceEnum.BUNGAE.value,
            writer=str(root.data.shop.uid),
        )
