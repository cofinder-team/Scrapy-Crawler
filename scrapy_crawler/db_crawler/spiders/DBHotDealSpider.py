import logging
import scrapy
from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy_crawler.db_crawler.items import DBItem, DBItemPrice
import json


class DBHotDealSpider(scrapy.Spider):
    name = "DBHotDealSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.db_crawler.pipelines.HotDealClassifierPipeline": 1,
            "scrapy_crawler.db_crawler.pipelines.SlackAlertPipeline": 2,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = PostgresClient()
        self.cur = self.conn.getCursor()
        self.cache = dict()

    def get_classified_items(self):
        self.cur.execute("SELECT * "
                         "FROM macguider.raw_used_item "
                         "WHERE type is not NULL AND item_id is not NULL AND classified = TRUE "
                         "AND date >= '2023-07-14'"
                         "ORDER BY date ")
        return self.cur.fetchall()

    def start_requests(self):
        unclassified_items = self.get_classified_items()

        for row in unclassified_items:
            if (row[9], row[10], row[13]) in self.cache:
                logging.info(f"Cache hit: {row[9]}, {row[10]}, {row[13]}")
                yield DBItemPrice(
                    id=row[0],
                    writer=row[1],
                    title=row[2],
                    content=row[3],
                    price=row[4],
                    source=row[5],
                    date=row[6],
                    url=row[7],
                    img_url=row[8],
                    type="NONE",
                    item_id=row[10],
                    average=self.cache[(row[9], row[10], row[13])]['average'],
                    low_price=self.cache[(row[9], row[10], row[13])]['price_20'],
                    high_price=self.cache[(row[9], row[10], row[13])]['price_80'],
                )
            else:
                yield scrapy.Request(
                    url=f"https://dev-api.macguider.io/price/deal/{row[9]}/{row[10]}?unused={'true' if row[13] else 'false'}",
                    callback=self.parse, meta={'db_item': row})

    def parse(self, response, **kwargs):
        item = response.meta['db_item']
        average = json.loads(response.text)['average']
        low_price = json.loads(response.text)['price_20']
        high_price = json.loads(response.text)['price_80']
        self.cache[(item[9], item[10], item[13])] = {
            'average': average,
            'price_20': low_price,
            'price_80': high_price,
        }

        yield DBItemPrice(
            id=item[0],
            writer=item[1],
            title=item[2],
            content=item[3],
            price=item[4],
            source=item[5],
            date=item[6],
            url=item[7],
            img_url=item[8],
            type="NONE",
            item_id=item[10],
            average=average if average else 0,
            low_price=low_price if low_price else 0,
            high_price=high_price if high_price else 0,
        )
