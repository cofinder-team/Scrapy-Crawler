import logging

from bs4 import BeautifulSoup
from itemadapter import ItemAdapter
from scrapy import Selector
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db.models import RawUsedItem
from scrapy_crawler.common.db.settings import get_engine
from scrapy_crawler.common.utils import (
    has_forbidden_keyword,
    save_image_from_url,
    too_long_text,
    too_low_price,
)
from scrapy_crawler.Joonggonara.utils import is_used_item

"""
    Scrapy Item : ArticleItem
    SQLAlchemy Model : RawUsedItem

    Pipeline List
    1. DuplicateFilterPipeline - 중복 필터링
    2. ManualFilterPipeline - 키워드, 가격, 중고나라에서 제공하는 상태 기반 필터링
    3. HtmlParserPipeline - HTML 파싱
    4. PostgresExportPipeline - Postgres DB에 저장
"""


class DuplicateFilterPipeline:
    name = "DuplicateFilterPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def is_duplicated(self, adapter: ItemAdapter) -> bool:
        try:
            item = (
                self.session.query(RawUsedItem)
                .filter(RawUsedItem.url == adapter["url"])
                .first()
            )
            return item is not None

        except Exception as e:
            logging.error(e)
            self.session.rollback()
            return False

    def process_item(self, item, spider):
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )
        adapter = ItemAdapter(item)

        if self.is_duplicated(adapter):
            spider.logger.info(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] Duplicate item found"
            )
            raise DropItem("Duplicate item found: %s" % item["url"].split("/")[-1])

        return item


class ManualFilterPipeline:
    name = "ManualFilterPipeline"

    def process_item(self, item, spider):
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )
        adapter = ItemAdapter(item)

        title, content, price, condition = (
            adapter["title"],
            adapter["content"],
            adapter["price"],
            adapter["product_condition"],
        )

        if has_forbidden_keyword(title + content):
            spider.logger.info(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] Forbidden word found"
            )
            raise DropItem("Forbidden word found: %s" % item["title"])

        if too_low_price(price):
            spider.logger.info(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] Too low price"
            )
            raise DropItem("Too low price: %s" % item["price"])

        if is_used_item(condition):
            spider.logger.info(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] Used item"
            )
            raise DropItem("Used item: %s" % item["url"].split("/")[-1])

        if too_long_text(content):
            spider.logger.info(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] Too long text"
            )
            raise DropItem("Too long text: %s" % item["url"].split("/")[-1])

        return item


class HtmlParserPipeline:
    name = "HtmlParserPipeline"

    def process_item(self, item, spider):
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )
        adapter = ItemAdapter(item)

        selector = Selector(text=adapter["content"])

        content = BeautifulSoup(
            "\n".join(selector.css(".se-text-paragraph > span").getall()),
            features="lxml",
        ).get_text()

        lines = content.split("\n")
        filtered_lines = []
        for line in lines:
            line = line.strip()
            if (
                not line.startswith("👆")
                and not line.startswith("※")
                and not line.startswith("상단 중고나라")
                and not line.startswith("위에 다운로드 ")
                and not line.startswith("──")
            ):
                filtered_lines.append(line)

        content = "\n".join(filtered_lines).replace("​", "")

        item["content"] = content

        # images = selector.css(".se-image-resource::attr(src)").getall()
        # item["content"] = content + "\n[Image URLS]\n" + "\n".join(images)

        return item


class PostgresExportPipeline:
    name = "PostgresExportPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )
        adapter = ItemAdapter(item)

        try:
            image = save_image_from_url(adapter["img_url"] + "?type=w300")

            self.session.add(
                RawUsedItem(
                    writer=adapter["writer"],
                    title=adapter["title"],
                    content=adapter["content"],
                    price=adapter["price"],
                    date=adapter["date"],
                    url=adapter["url"],
                    img_url=adapter["img_url"],
                    source=adapter["source"],
                    image=image.getvalue(),
                    raw_json=adapter["raw_json"],
                )
            )
            self.session.commit()
            spider.logger.info(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] item saved"
            )
        except Exception as e:
            spider.logger.error(
                f"[{type(self).__name__}][{item['url'].split('/')[-1]}] item save failed with error: {e}"
            )
            self.session.rollback()

        return item
