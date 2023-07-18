import scrapy
from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy_crawler.db_crawler.items import DBItem


class DBHotDealSpider(scrapy.Spider):
    name = "DBHotDealSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = PostgresClient()
        self.cur = self.conn.getCursor()

    def get_classified_items(self):
        self.cur.execute("SELECT * "
                         "FROM macguider.raw_used_item "
                         "WHERE type is not NULL AND item_id is not NULL AND classified = TRUE"
                         "AND date >= '2023-07-14'"
                         "ORDER BY date ")
        return self.cur.fetchall()

    def start_requests(self):
        unclassified_items = self.get_classified_items()

        for row in unclassified_items:
            yield scrapy.Request(url=f"https://dev-api.macguider.io/item/{row[10]}/{row[11]}", callback=self.parse, meta={'item': row})

    def parse(self, response, **kwargs):
        item = response.meta['item']

        yield DBItem()
