import logging

from bs4 import BeautifulSoup
from itemadapter import ItemAdapter
from scrapy import Selector

from scrapy_crawler.common.db.models import RawUsedItem
from scrapy_crawler.common.utils import (
    has_forbidden_keyword,
    save_image_from_url,
    too_low_price,
)
from scrapy_crawler.common.utils.custom_exceptions import (
    DropDuplicateItem,
    DropForbiddenKeywordItem,
    DropTooLowPriceItem,
)
from scrapy_crawler.Joonggonara.TotalSearch.spiders.JgKeywordSpider import (
    JgKeywordSpider,
)

"""
    Scrapy Item : ArticleItem
    SQLAlchemy Model : RawUsedItem

    Pipeline List
    1. DuplicateFilterPipeline - 중복 필터링
    2. ManualFilterPipeline - 키워드, 가격, 중고나라에서 제공하는 상태 기반 필터링
    3. HtmlParserPipeline - HTML 파싱
    4. PostgresExportPipeline - Postgres DB에 저장
"""


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


class DuplicateFilterPipeline:
    name = "DuplicateFilterPipeline"

    def __init__(self):
        self.session = None

    def is_duplicated(self, adapter: ItemAdapter) -> bool:
        try:
            item = (
                self.session.query(RawUsedItem)
                .filter(
                    RawUsedItem.url == adapter["url"]
                    or RawUsedItem.title == adapter["title"]
                )
                .first()
            )
            return item is not None

        except Exception as e:
            logging.error(e)
            self.session.rollback()
            return False

    def process_item(self, item, spider: JgKeywordSpider):
        self.session = spider.session
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )
        adapter = ItemAdapter(item)

        if self.is_duplicated(adapter):
            raise DropDuplicateItem(
                "Duplicate item found: %s" % item["url"].split("/")[-1]
            )

        return item


class ManualFilterPipeline:
    name = "ManualFilterPipeline"

    def process_item(self, item, spider):
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )
        adapter = ItemAdapter(item)

        title, content, price = (
            adapter["title"],
            adapter["content"],
            adapter["price"],
        )

        if has_forbidden_keyword(title + content):
            raise DropForbiddenKeywordItem("Forbidden word found: %s" % item["title"])

        if too_low_price(price):
            raise DropTooLowPriceItem("Too low price: %s" % item["price"])

        return item



    def process_item(self, item, spider):
        spider.logger.info(
            f"[{type(self).__name__}][{item['url'].split('/')[-1]}] start process_item"
        )


        return item


class PostgresExportPipeline:
    name = "PostgresExportPipeline"

    def __init__(self):
        self.session = None

    def process_item(self, item, spider: JgKeywordSpider):
        self.session = spider.session
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
