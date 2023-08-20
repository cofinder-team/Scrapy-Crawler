import ast
import json
from typing import List
from urllib import parse

import scrapy

from scrapy_crawler.Bungae.metadata.article import ArticleRoot
from scrapy_crawler.Bungae.metadata.total_search import BgList, TotalSearchRoot
from scrapy_crawler.Bungae.TotalSearch.items import ArticleItem
from scrapy_crawler.common.enums import SourceEnum
from scrapy_crawler.common.utils.constants import BunJang
from scrapy_crawler.common.utils.helpers import init_cloudwatch_logger


class BgKeywordListSpider(scrapy.Spider):
    name = "BgKeywordListSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Bungae.TotalSearch.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.Bungae.TotalSearch.pipelines.PostgresExportPipeline": 3,
        }
    }

    def __init__(self, keywords=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_cloudwatch_logger(self.name)
        self.keywords = ast.literal_eval(keywords)

    def start_requests(self):
        for keyword in self.keywords:
            self.logger.info(f"Start crawling keyword: {keyword}")
            yield scrapy.Request(
                BunJang.TOTAL_SEARCH_API_URL % parse.quote(keyword), self.parse
            )

    def parse(self, response):
        root = TotalSearchRoot.from_dict(json.loads(response.text))
        articles: List[BgList] = root.list

        for article in articles:
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
