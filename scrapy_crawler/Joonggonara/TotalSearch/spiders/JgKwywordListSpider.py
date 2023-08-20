import ast
import html
import json
from urllib import parse

import scrapy

from scrapy_crawler.common.enums import SourceEnum
from scrapy_crawler.common.utils import to_local_timestring
from scrapy_crawler.common.utils.constants import Joonggonara
from scrapy_crawler.common.utils.helpers import init_cloudwatch_logger
from scrapy_crawler.Joonggonara.metadata.article import ArticleRoot
from scrapy_crawler.Joonggonara.metadata.total_search import TotalSearchRoot
from scrapy_crawler.Joonggonara.TotalSearch.items import ArticleItem
from scrapy_crawler.Joonggonara.utils.helpers import is_official_seller, is_selling


class JgKeywordListSpider(scrapy.Spider):
    name = "JgKeywordListSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.HtmlParserPipeline": 3,
            "scrapy_crawler.Joonggonara.TotalSearch.pipelines.PostgresExportPipeline": 4,
        }
    }

    def __init__(self, keywords=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_cloudwatch_logger(self.name)
        self.keywords: list = ast.literal_eval(keywords)

    def start_requests(self):
        for keyword in self.keywords:
            self.logger.info(f"Start crawling keyword: {keyword}")
            yield scrapy.Request(
                Joonggonara.TOTAL_SEARCH_FETCH_URL % parse.quote(keyword), self.parse
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
            yield scrapy.Request(
                Joonggonara.ARTICLE_API_URL % article.articleId,
                callback=self.parse_article,
                meta={"article_url": Joonggonara.ARTICLE_URL % article.articleId},
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
