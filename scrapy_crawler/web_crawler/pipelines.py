import logging

from bs4 import BeautifulSoup
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.selector import Selector
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.util.db.models import RawUsedItem
from scrapy_crawler.util.db.settings import get_engine


class DuplicateFilterPipeline:
    name = "DuplicateFilterPipeline"

    def __init__(self):
        self.Session = sessionmaker(bind=get_engine())
        self.session = self.Session()

    def is_duplicated(self, adapter: ItemAdapter) -> bool:
        item = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.url == adapter["url"])
            .filter(
                RawUsedItem.writer == adapter["writer"]
                and RawUsedItem.title == adapter["title"]
            )
            .first()
        )

        return item is not None

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if self.is_duplicated(adapter):
            raise DropItem("Duplicate item found: %s" % item)
        return item


class ContentScraperPipeline:
    name = "ContentScraperPipeline"

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        selector = Selector(text=adapter["content"])

        content = (
            BeautifulSoup("\n".join(selector.css(".se-text-paragraph > span").getall()))
            .get_text()
            .replace("​", "")
            .replace("👆중고나라 앱이 있다는 걸 아시나요?", "")
            .replace("상단 중고나라 앱 다운받기 클릭!", "")
            .replace("👆앱에서 구매를 원하는 댓글이 달릴 수도 있어요! 더보기 클릭하고 미리 알아두기!", "")
            .replace(
                "※ 등록한 게시글이 회원의 신고를 받거나 이상거래로 모니터링 될 경우 중고나라 사기통합조회 DB로 수집/활용될 수 있습니다.",
                "",
            )
            .replace("※ 유튜브, 블로그, 인스타그램 등 상품 정보 제공 목적 링크 가능(외부 거래를 유도하는 링크 제외) ", "")
            .replace("─", "")
            .replace("\n\n", "")
        )

        images = selector.css(".se-image-resource::attr(src)").getall()

        item["content"] = content + "\n[Image URLS]\n" + "\n".join(images)

        return item


class ManualFilterPipeline:
    name = "ManualFilterPipeline"

    def __init__(self):
        self.forbidden_words = ["매입", "삽니다", "교환", "파트너"]
        self.price_threshold = 200000

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        title = adapter["title"]
        price = adapter["price"]
        content = adapter["content"]

        if self.forbidden_words in title or self.forbidden_words in content:
            raise DropItem("Forbidden word found: %s" % item)

        if price <= self.price_threshold:
            raise DropItem("Price is too low: %s" % item)

        return item


class PostgresPipeline:
    name = "postgres_pipeline"

    def __init__(self):
        self.session = sessionmaker(bind=get_engine())()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        try:
            self.session.add(
                RawUsedItem(
                    url=adapter["url"],
                    img_url=adapter["img_url"],
                    price=adapter["price"],
                    date=adapter["date"],
                    writer=adapter["writer"],
                    title=adapter["title"],
                    content=adapter["content"],
                    source="중고나라",
                )
            )
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

        return item
