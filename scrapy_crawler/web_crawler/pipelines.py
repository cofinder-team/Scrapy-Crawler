# -*- coding: utf-8 -*-
import logging

from bs4 import BeautifulSoup
from itemadapter import ItemAdapter

from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy.exceptions import DropItem
from scrapy.selector import Selector


class DuplicateFilterPipeline:
    name = "DuplicateFilterPipeline"

    def __init__(self):
        self.db = PostgresClient()
        self.cur = self.db.getCursor()

    def url_already_exists(self, url):
        self.cur.execute("SELECT * FROM macguider.raw_used_item WHERE url = %s", (url,))
        return self.cur.fetchone()

    def title_already_exists(self, title):
        self.cur.execute("SELECT * FROM macguider.raw_used_item WHERE title = %s", (title,))
        return self.cur.fetchone()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if self.url_already_exists(adapter["url"]) or self.title_already_exists(adapter["title"]):
            raise DropItem("Duplicate item found: %s" % item)
        return item


class ContentScraperPipeline:
    name = "ContentScraperPipeline"

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        selector = Selector(text=adapter["content"])

        content = BeautifulSoup("\n".join(selector.css(".se-text-paragraph > span").getall())).get_text() \
            .replace("​", "") \
            .replace("👆중고나라 앱이 있다는 걸 아시나요? 상단 중고나라 앱 다운받기 클릭!", "") \
            .replace("👆앱에서 구매를 원하는 댓글이 달릴 수도 있어요! 더보기 클릭하고 미리 알아두기!", "") \
            .replace("※ 등록한 게시글이 회원의 신고를 받거나 이상거래로 모니터링 될 경우 중고나라 사기통합조회 DB로 수집/활용될 수 있습니다.", "") \
            .replace("─", "").replace("\n\n", "")

        images = selector.css(".se-image-resource::attr(src)").getall()

        item["content"] = content + "\n[Image URLS]\n" + "\n".join(images)

        return item


class PostgresPipeline:
    name = "postgres_pipeline"

    def __init__(self):
        self.db = PostgresClient()
        self.cur = self.db.getCursor()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        try:
            self.cur.execute(
                "INSERT INTO macguider.raw_used_item (url, img_url, price, date, writer, title, content, source) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (adapter["url"], adapter["img_url"], adapter["price"], adapter["date"], adapter["writer"],
                 adapter["title"], adapter["content"], "중고나라"))
            self.db.commit()
        except Exception as e:
            logging.error(e)
            self.db.rollback()

        return item
