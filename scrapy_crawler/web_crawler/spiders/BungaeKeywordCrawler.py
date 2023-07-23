import json
from urllib import parse

import scrapy

from scrapy_crawler.web_crawler.items import BungaeArticle, BungaeArticleDetail


class BungaeKeywordCrawler(scrapy.Spider):
    name = "BungaeKeywordCrawler"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.web_crawler.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.web_crawler.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.web_crawler.pipelines.PostgresPipeline": 3,
        }
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword

    def start_requests(self):
        yield scrapy.Request(
            f"https://api.bunjang.co.kr/api/1/find_v2.json"
            f"?q={parse.quote(self.keyword)}&order=date&n=100&page=0&n=100",
            self.parse_search,
        )

    def parse_search(self, response):
        articles = json.loads(response.text)["list"]

        for article_json in articles:
            article: BungaeArticle = BungaeArticle(
                **{key: article_json[key] for key in BungaeArticle.fields.keys()}
            )
            print(article.__dict__)
            yield scrapy.Request(
                f"https://api.bunjang.co.kr/api/pms/v2/products-detail/{article['pid']}?viewerUid=-1",
                callback=self.parse_article,
            )

    def parse_article(self, response):
        product_json = json.loads(response.text)["data"]["product"]
        shop_json = json.loads(response.text)["data"]["shop"]
        product_json["source"] = "번개장터"
        product_json["writer"] = shop_json["uid"]

        yield BungaeArticleDetail(
            **{key: product_json[key] for key in BungaeArticleDetail.fields.keys()}
        )
