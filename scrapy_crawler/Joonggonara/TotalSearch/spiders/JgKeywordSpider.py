import html
import json
from urllib import parse

import boto3
import scrapy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm import sessionmaker
from twisted.python.failure import Failure

from scrapy_crawler.common.db import get_engine
from scrapy_crawler.common.db.models import LogCrawler
from scrapy_crawler.common.enums import SourceEnum
from scrapy_crawler.common.slack.SlackBots import ExceptionSlackBot
from scrapy_crawler.common.utils import to_local_timestring
from scrapy_crawler.common.utils.constants import Joonggonara
from scrapy_crawler.common.utils.helpers import get_local_timestring
from scrapy_crawler.Joonggonara.metadata.article import ArticleRoot
from scrapy_crawler.Joonggonara.metadata.total_search import TotalSearchRoot
from scrapy_crawler.Joonggonara.TotalSearch.items import ArticleItem
from scrapy_crawler.Joonggonara.utils.helpers import is_official_seller, is_selling


class JgKeywordSpider(scrapy.Spider):
    name = "JgKeywordSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.HtmlParserPipeline": 1,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.DuplicateFilterPipeline": 3,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.PublishSQSPipeline": 4,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.PostgresExportPipeline": 5,
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
                    source=SourceEnum.JOONGGONARA.value,
                    item_status=f"DROPPED_{exception.__class__.__name__}",
                    url=item["url"],
                    created_at=get_local_timestring(),
                )
            )

            self.session.commit()
        except Exception as e:
            self.logger.error(e)
            self.session.rollback()

    def start_requests(self):
        self.logger.info(f"Start crawling keyword: {self.keyword}")
        yield scrapy.Request(
            Joonggonara.TOTAL_SEARCH_FETCH_URL % parse.quote(self.keyword), self.parse
        )

    def parse(self, response):
        json_response = json.loads(response.text)
        root = TotalSearchRoot.from_dict(json_response)

        target_articles = list(
            filter(
                lambda x: is_selling(x),
                filter(
                    lambda x: not is_official_seller(x), root.message.result.articleList
                ),
            )
        )

        self.logger.info(f"Found {len(target_articles)} articles")
        for article in target_articles:
            article_url = Joonggonara.ARTICLE_URL % article.articleId

            if self.item_already_crawled(article_url):
                continue

            yield scrapy.Request(
                Joonggonara.ARTICLE_API_URL % article.articleId,
                callback=self.parse_article,
                meta={"article_url": article_url},
            )

    def parse_article(self, response):
        url = response.meta["article_url"]
        root = ArticleRoot.from_dict(json.loads(response.text))

        title = root.result.article.subject
        writer = root.result.article.writer.id
        content = html.unescape(root.result.article.contentHtml)
        price = root.result.saleInfo.price
        img_url = root.result.saleInfo.image.url
        date = to_local_timestring(root.result.article.writeDate // 1000)
        status = root.result.saleInfo.productCondition
        raw_json = json.loads(response.text)
        product_condition = root.result.saleInfo.productCondition

        yield ArticleItem(
            url=url,
            title=title,
            writer=writer,
            content=content,
            price=price,
            img_url=img_url,
            date=date,
            status=status,
            source=SourceEnum.JOONGGONARA.value,
            raw_json=raw_json,
            product_condition=product_condition,
        )
