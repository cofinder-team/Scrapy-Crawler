import html
import json
from urllib import parse

import scrapy
from scrapy import signals
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import get_engine
from scrapy_crawler.common.db.models import DroppedItem, RawUsedItem
from scrapy_crawler.common.enums import SourceEnum
from scrapy_crawler.common.utils import to_local_timestring
from scrapy_crawler.common.utils.constants import Joonggonara
from scrapy_crawler.common.utils.helpers import (
    exception_to_category_code,
    get_local_timestring,
    init_cloudwatch_logger,
)
from scrapy_crawler.Joonggonara.metadata.article import ArticleRoot
from scrapy_crawler.Joonggonara.metadata.total_search import TotalSearchRoot
from scrapy_crawler.Joonggonara.TotalSearch.items import ArticleItem
from scrapy_crawler.Joonggonara.utils.helpers import is_official_seller, is_selling


class JgKeywordSpider(scrapy.Spider):
    name = "JgKeywordSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.HtmlParserPipeline": 3,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.PostgresExportPipeline": 4,
        }
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_cloudwatch_logger(self.name)
        self.session = sessionmaker(bind=get_engine())()
        self.keyword = keyword

    def close_spider(self, spider):
        self.session.close()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.item_dropped, signal=signals.item_dropped)
        return spider

    def item_already_dropped(self, url) -> bool:
        return (
            self.session.query(DroppedItem)
            .filter(DroppedItem.source == SourceEnum.JOONGGONARA.value)
            .filter(DroppedItem.url == url)
            .first()
            is not None
        )

    def item_already_crawled(self, url) -> bool:
        return (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.url == url)
            .filter(RawUsedItem.source == SourceEnum.JOONGGONARA.value)
            .first()
            is not None
        )

    def item_dropped(self, item, response, exception, spider):
        if self.item_already_dropped(item["url"]) or (
            (category_code := exception_to_category_code(exception)) is None
        ):
            return

        self.logger.info(f"Item dropped: {exception.__class__.__name__}")

        try:
            self.session.add(
                DroppedItem(
                    source=SourceEnum.JOONGGONARA.value,
                    category=category_code,
                    url=item["url"],
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

            if self.item_already_crawled(article_url) or self.item_already_dropped(
                article_url
            ):
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
