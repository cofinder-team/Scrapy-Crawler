import datetime
import html
import json
from urllib import parse

import scrapy
from scrapy.exceptions import DropItem

from scrapy_crawler.web_crawler.items import JgArticle


class JgKeywordCrawler(scrapy.Spider):
    name = "JgKeywordCrawler"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.web_crawler.pipelines.DuplicateFilterPipeline": 1,
            "scrapy_crawler.web_crawler.pipelines.ContentScraperPipeline": 2,
            "scrapy_crawler.web_crawler.pipelines.ManualFilterPipeline": 2,
            "scrapy_crawler.web_crawler.pipelines.PostgresPipeline": 4,
        }
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword

    def start_requests(self):
        yield scrapy.Request(
            "https://apis.naver.com/cafe-web/cafe-mobile/CafeMobileWebArticleSearchListV3"
            + f"?cafeId=10050146&query={parse.quote(self.keyword)}"
            + "&searchBy=1&sortBy=date&page=1&perPage=30&adUnit=MW_CAFE_BOARD",
            self.parse,
        )

    def parse(self, response):
        res = json.loads(response.text)["message"]["result"]["articleList"]

        non_sellers = list(filter(lambda x: x["memberLevel"] != 150, res))
        selling_articles = list(
            filter(
                lambda x: x["productSale"]["saleStatus"] == "SALE"
                or x["productSale"]["saleStatus"] == "ESCROW",
                non_sellers,
            )
        )

        for article in selling_articles:
            yield scrapy.Request(
                f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/10050146/articles/{article['articleId']}",
                callback=self.parse_article,
                meta={
                    "article_url": f"https://cafe.naver.com/joonggonara/{article['articleId']}"
                },
            )

    def parse_article(self, response):
        saleInfo = json.loads(response.text)["result"]["saleInfo"]
        article = json.loads(response.text)["result"]["article"]

        url = response.meta["article_url"]
        title = article["subject"]
        writer = article["writer"]["id"]
        product_status = (
            saleInfo["productCondition"] if "productCondition" in saleInfo else "EMPTY"
        )

        # Convert timestamp to local datetime
        date = (
            datetime.datetime.fromtimestamp(article["writeDate"] / 1000)
            + datetime.timedelta(hours=9)
        ).strftime("%Y-%m-%d %H:%M:%S")

        # Convert escaped html to normal html
        content = html.unescape(article["contentHtml"])

        price = saleInfo["price"]
        img_url = saleInfo["image"]["url"]

        if product_status == "USED":
            raise DropItem("A ranked product")

        yield JgArticle(
            url=url,
            title=title,
            writer=writer,
            date=date,
            content=content,
            price=price,
            img_url=img_url,
            source="중고나라",
        )
