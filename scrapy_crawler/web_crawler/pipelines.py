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
        self.session = sessionmaker(bind=get_engine())()

    def is_duplicated(self, adapter: ItemAdapter) -> bool:
        item = None
        source = adapter["source"]

        if source == "중고나라":
            item = (
                self.session.query(RawUsedItem)
                .filter(RawUsedItem.url == adapter["url"])
                .first()
            )
        elif source == "번개장터":
            item = (
                self.session.query(RawUsedItem)
                .filter(
                    RawUsedItem.url
                    == f"https://api.bunjang.co.kr/api/pms/v2/products-detail/{adapter['pid']}?viewerUid=-1"
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
        self.forbidden_words = ["매입", "삽니다", "파트너"]
        self.price_threshold = 200000

    def has_forbidden_word(self, title: str, content: str) -> bool:
        return any(word in title for word in self.forbidden_words) or any(
            word in content for word in self.forbidden_words
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        source = adapter["source"]
        title: str = ""
        content: str = ""

        if source == "번개장터":
            title = adapter["name"]
            content = adapter["description"]
        elif source == "중고나라":
            title = adapter["title"]
            content = adapter["content"]
        price = adapter["price"]

        if self.has_forbidden_word(title, content):
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
        source = adapter["source"]
        url, img_url, price, date, writer, title, content = "", "", "", "", "", "", ""

        if source == "번개장터":
            url = f"https://api.bunjang.co.kr/api/pms/v2/products-detail/{adapter['pid']}?viewerUid=-1"
            img_url = adapter["imageUrl"]
            price = adapter["price"]
            date = adapter["updatedAt"]
            writer = adapter["writer"]
            title = adapter["name"]
            content = adapter["description"]
        elif source == "중고나라":
            url = adapter["url"]
            img_url = adapter["img_url"]
            price = adapter["price"]
            date = adapter["date"]
            writer = adapter["writer"]
            title = adapter["title"]
            content = adapter["content"]

        try:
            self.session.add(
                RawUsedItem(
                    url=url,
                    img_url=img_url,
                    price=price,
                    date=date,
                    writer=writer,
                    title=title,
                    content=content,
                    source=source,
                )
            )
            self.session.commit()
        except Exception as e:
            logging.error(e)
            self.session.rollback()

        return item
