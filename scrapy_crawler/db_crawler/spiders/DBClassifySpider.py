import scrapy
from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy_crawler.db_crawler.items import DBItem


class DBClassifySpider(scrapy.Spider):
    name = "DBClassifySpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.db_crawler.pipelines.CategoryClassifierPipeline": 1,
            "scrapy_crawler.db_crawler.pipelines.MacbookModelClassifierPipeline": 2,
            "scrapy_crawler.db_crawler.pipelines.ChipClassifierPipeline": 3,
            "scrapy_crawler.db_crawler.pipelines.MacbookRamSSDClassifierPipeline": 4,
            "scrapy_crawler.db_crawler.pipelines.IpadModelClassifierPipeline": 5,
            "scrapy_crawler.db_crawler.pipelines.IpadGenerationClassifierPipeline": 6,
            "scrapy_crawler.db_crawler.pipelines.IpadStorageClassifierPipeline": 7,
            "scrapy_crawler.db_crawler.pipelines.IpadCellularClassifierPipeline": 8,
            "scrapy_crawler.db_crawler.pipelines.UnusedClassifierPipeline": 9,
            "scrapy_crawler.db_crawler.pipelines.AppleCarePlusClassifierPipeline": 10,
            "scrapy_crawler.db_crawler.pipelines.DBExportPipeline": 11,
            "scrapy_crawler.db_crawler.pipelines.SlackAlertPipeline": 12,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = PostgresClient()
        self.cur = self.conn.getCursor()

    def get_unclassified_items(self):
        self.cur.execute("SELECT * "
                         "FROM macguider.raw_used_item "
                         "WHERE classified = FALSE "
                         "AND type is NULL AND item_id is NULL "
                         "AND date >= '2023-07-14'"
                         "ORDER BY date ")
        return self.cur.fetchall()

    def start_requests(self):
        # Fake fetch
        yield scrapy.Request(url="https://www.google.com", callback=self.parse)

    def parse(self, response, **kwargs):
        unclassified_items = self.get_unclassified_items()

        for row in unclassified_items:
            yield DBItem(
                id=row[0],
                writer=row[1],
                title=row[2],
                content=row[3],
                price=row[4],
                source=row[5],
                date=row[6],
                url=row[7],
                img_url=row[8],
                type=row[9],
                item_id=row[10]
            )
