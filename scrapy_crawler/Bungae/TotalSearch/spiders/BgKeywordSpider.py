import json
from typing import List
from urllib import parse

import boto3
import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import sessionmaker
from twisted.python.failure import Failure

from scrapy_crawler.Bungae.metadata.article import ArticleRoot
from scrapy_crawler.Bungae.metadata.total_search import BgList, TotalSearchRoot
from scrapy_crawler.Bungae.TotalSearch.items import ArticleItem
from scrapy_crawler.common.db import get_engine
from scrapy_crawler.common.db.models import LogCrawler
from scrapy_crawler.common.enums import SourceEnum
from scrapy_crawler.common.slack.SlackBots import ExceptionSlackBot
from scrapy_crawler.common.utils.constants import BunJang
from scrapy_crawler.common.utils.helpers import get_local_timestring


class BgKeywordSpider(scrapy.Spider):
    name = "BgKeywordSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Bungae.TotalSearch.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.PublishSQSPipeline": 3,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.PostgresExportPipeline": 4,
        }
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = get_project_settings()
        sqs = boto3.resource(
            "sqs",
            aws_access_key_id=settings["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=settings["AWS_SECRET_ACCESS_KEY"],
            region_name=settings["AWS_REGION_NAME"],
        )

        self.live_queue = sqs.get_queue_by_name(
            QueueName=settings["AWS_LIVE_QUEUE_NAME"]
        )
        self.session = sessionmaker(bind=get_engine())()
        self.exception_slack_bot: ExceptionSlackBot = ExceptionSlackBot()
        self.keyword = keyword

    def close_spider(self, spider):
        self.session.close()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(spider.item_error, signal=signals.item_error)
        return spider

    def item_error(self, item, response, spider, failure: Failure):
        self.exception_slack_bot.post_unhandled_message(
            spider.name, failure.getErrorMessage()
        )

    def item_already_crawled(self, url) -> bool:
        return (
            self.session.query(LogCrawler).filter(LogCrawler.url == url).first()
            is not None
        )

    def item_dropped(self, item, response, exception, spider):
        self.logger.info(f"Item dropped: {exception.__class__.__name__}")

        try:
            self.session.add(
                LogCrawler(
                    url=BunJang.ARTICLE_URL % str(item["pid"]),
                    crawled_at=get_local_timestring(),
                    source=SourceEnum.BUNGAE.value,
                    item_status=f"DROPPED_{exception.__class__.__name__}",
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
            if self.item_already_crawled(article_url):
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
