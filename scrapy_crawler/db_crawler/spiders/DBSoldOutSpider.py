import scrapy
from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy_crawler.db_crawler.items import DBItem, JgArticle
import json


class DBSoldOutSpider(scrapy.Spider):
    name = "DBSoldOutSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.db_crawler.pipelines.SoldOutClassifierPipeline": 1,
            "scrapy_crawler.db_crawler.pipelines.DBUpdateLastCrawledPipeline": 2,
            "scrapy_crawler.db_crawler.pipelines.SlackAlertPipeline": 3,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = PostgresClient()
        self.cur = self.conn.getCursor()

    def get_unsold_items(self):
        self.cur.execute(
            "SELECT * "
            "FROM macguider.deal "
            "WHERE sold = false "
            "ORDER BY last_crawled "
        )
        return self.cur.fetchall()

    def start_requests(self):
        unsold_items = self.get_unsold_items()

        for row in unsold_items:
            id = row[0]
            url = row[7].split("/")[-1]
            yield scrapy.Request(
                url=f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/10050146/articles/{url}",
                callback=self.parse,
                meta={"item_id": id},
            )

    def parse(self, response, **kwargs):
        # 글이 삭제된 경우
        if response.status == 404:
            yield JgArticle(id=response.meta["item_id"], price=0, status="SOLD_OUT")

        item_id = response.meta["item_id"]
        saleInfo = json.loads(response.text)["result"]["saleInfo"]

        price = saleInfo["price"]
        status = saleInfo["saleStatus"]

        yield JgArticle(id=item_id, price=price, status=status)
