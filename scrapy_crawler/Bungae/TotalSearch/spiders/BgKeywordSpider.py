import json
from typing import List
from urllib import parse

import scrapy

from scrapy_crawler.Bungae.metadata.article import ArticleRoot
from scrapy_crawler.Bungae.metadata.total_search import BgList, TotalSearchRoot
from scrapy_crawler.Bungae.TotalSearch.items import ArticleItem
from scrapy_crawler.Bungae.utils.constants import ARTICLE_API_URL, TOTAL_SEARCH_API_URL
from scrapy_crawler.common.utils.helpers import init_cloudwatch_logger


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
        self.keyword = keyword

    def start_requests(self):
        self.logger.info(f"Start crawling keyword: {self.keyword}")
        yield scrapy.Request(
            TOTAL_SEARCH_API_URL % parse.quote(self.keyword), self.parse
        )

    def parse(self, response):
        root = TotalSearchRoot.from_dict(json.loads(response.text))
        articles: List[BgList] = root.list

        for article in articles:
            yield scrapy.Request(
                ARTICLE_API_URL % article.pid,
                callback=self.parse_article,
            )

    def parse_article(self, response):
        root = ArticleRoot.from_dict(json.loads(response.text))
        yield ArticleItem(
            pid=root.data.product.pid,
            title=root.data.product.name,
            content=root.data.product.description,
            price=root.data.product.price,
            img_url=root.data.product.imageUrl.replace("{cnt}", "1").replace(
                "{res}", "300"
            ),
            prod_status=root.data.product.status,
            date=root.data.product.updatedAt,
            raw_json=json.loads(response.text),
            source="번개장터",
            writer=str(root.data.shop.uid),
        )
