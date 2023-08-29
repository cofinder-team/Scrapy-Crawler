import datetime
import logging
import re

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import null
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.chatgpt.CallBacks import CloudWatchCallbackHandler
from scrapy_crawler.common.chatgpt.chains import (
    apple_care_plus_chain,
    category_chain,
    unused_chain,
)
from scrapy_crawler.common.db import RawUsedItem, get_engine
from scrapy_crawler.common.db.models import Deal, ViewTrade
from scrapy_crawler.common.slack.SlackBots import LabelingSlackBot
from scrapy_crawler.common.utils import get_local_timestring
from scrapy_crawler.common.utils.constants import CONSOLE_URL, NEW_CONSOLE_URL
from scrapy_crawler.common.utils.custom_exceptions import (
    DropAndMarkItem,
    DropUnsupportedCategoryItem,
)
from scrapy_crawler.common.utils.helpers import item_to_type
from scrapy_crawler.DBWatchDog.items import IpadItem, IphoneItem, MacbookItem

cloudwatchCallbackHandler = CloudWatchCallbackHandler()


class CategoryClassifierPipeline:
    def __init__(self):
        self.chain = category_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )

        raw_result: str = self.chain.run(
            title=adapter["title"],
            callbacks=[
                cloudwatchCallbackHandler.set_meta_data(
                    log_stream_name=str(adapter["id"]),
                    function_name=type(self).__name__,
                )
            ],
        ).upper()

        result = re.search(r"IPAD|MAC|IPHONE", raw_result)

        if result:
            category = result.group().upper()

            if category == "MAC":
                return MacbookItem(**adapter)
            elif category == "IPAD":
                return IpadItem(**adapter)
            elif category == "IPHONE":
                return IphoneItem(**adapter)
            else:
                raise DropUnsupportedCategoryItem(result)
        else:
            raise DropUnsupportedCategoryItem("No category found")


class UnusedClassifierPipeline:
    def __init__(self):
        self.unused_chain = unused_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )

        title = adapter["title"]
        content = adapter["content"]

        regex = re.compile(r"미개봉|새상품")
        if regex.search(title + content) is not None:
            predict = unused_chain.run(
                title=title,
                content=content,
                callbacks=[
                    cloudwatchCallbackHandler.set_meta_data(
                        log_stream_name=str(adapter["id"]),
                        function_name=type(self).__name__,
                    )
                ],
            )

            adapter["unused"] = "TRUE" in predict.upper()
        else:
            adapter["unused"] = False

        return item


class AppleCarePlusClassifierPipeline:
    def __init__(self):
        self.apple_care_plus_chain = apple_care_plus_chain
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )
        title = adapter["title"]
        content = adapter["content"]

        regex = re.compile(r"애플케어플러스|애케플|애캐플|케어|캐어|CARE")

        if regex.search(title + content) is not None:
            predict = self.apple_care_plus_chain.run(
                title=title,
                content=content,
                callbacks=[
                    cloudwatchCallbackHandler.set_meta_data(
                        log_stream_name=str(adapter["id"]),
                        function_name=type(self).__name__,
                    )
                ],
            )

            apple_care = "TRUE" in predict.upper()
        else:
            apple_care = False

        adapter["apple_care_plus"] = apple_care
        return item


class PersistRawUsedItemPipeline:
    name = "PersistRawUsedItemPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )
        try:
            item_id = adapter["item_id"]
            item_type = item_to_type(item).value
            unused = adapter["unused"]

            logging.error(
                f"[{type(self).__name__}][{item['id']}] item_type: {item_type}, item_id: {item_id}, unused: {unused}"
            )

            self.session.query(RawUsedItem).filter(
                RawUsedItem.id == adapter["id"]
            ).update(
                {
                    RawUsedItem.type: item_type,
                    RawUsedItem.item_id: adapter["item_id"],
                    RawUsedItem.unused: adapter["unused"],
                }
            )

            self.session.commit()
            return item
        except Exception as e:
            self.session.rollback()
            raise DropAndMarkItem(f"[{type(self).__name__}][{item['id']}] {e}")


class LabelingAlertPipeline:
    name = "LabelingAlertPipeline"

    def __init__(self):
        self.slack_bot = LabelingSlackBot()
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def has_multiple_generation(self, item) -> bool:
        title = item["title"]
        content = item["content"]
        pattern = re.compile(r"\d세대")
        keywords = set(pattern.findall(title + content))

        return len(keywords) > 1

    def is_abnormal_price(self, item: MacbookItem | IpadItem | IphoneItem) -> bool:
        item_id = item["item_id"]
        item_type = "P" if isinstance(item, IpadItem) else "M"
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        price = item["price"]

        try:
            entity: ViewTrade = (
                self.session.query(ViewTrade)
                .filter(ViewTrade.id == item_id)
                .filter(ViewTrade.type == item_type)
                .filter(ViewTrade.date == today)
                .filter(ViewTrade.source == null())
                .first()
            )

            average_price = entity.average
            return (price <= average_price * 0.75) or (price >= average_price * 1.25)
        except Exception as e:
            logging.error(f"[{type(self).__name__}][{item['id']}] {e}")
            return True

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )
        # Temporarily disable alert
        if isinstance(item, IphoneItem):
            return item

        alert_msgs = []
        if self.has_multiple_generation(item):
            alert_msgs.append("모델 분류 확인")

        if self.is_abnormal_price(item):
            alert_msgs.append("모델/상태 분류 확인")

        if len(alert_msgs) > 0:
            msgs = " && ".join(alert_msgs)
            self.slack_bot.post_hotdeal_message(
                console_url=CONSOLE_URL % adapter["id"],
                source=adapter["source"],
                msg=msgs,
            )

            # Stop pipeline
            raise DropItem(f"[{type(self).__name__}][{item['id']}] {msgs}")

        return item


class PersistDealPipeline:
    name = "PersistDealPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )

        item_type = item_to_type(item).value
        try:
            # Get RawUsedItem
            entity: RawUsedItem = (
                self.session.query(RawUsedItem)
                .filter(RawUsedItem.id == adapter["id"])
                .first()
            )

            # Delete all duplicated deals
            self.session.query(Deal).filter(Deal.item_id == entity.item_id).filter(
                Deal.type == item_type
            ).filter(Deal.unused == entity.unused).filter(
                Deal.writer == entity.writer
            ).filter(
                Deal.source == entity.source
            ).update(
                {Deal.deleted_at: get_local_timestring()}
            )

            # Insert to Deal
            self.session.add(
                Deal(
                    type=item_type,
                    item_id=entity.item_id,
                    price=entity.price,
                    date=entity.date,
                    unused=entity.unused,
                    source=entity.source,
                    url=entity.url,
                    title=entity.title,
                    content=entity.content,
                    writer=entity.writer,
                    image=entity.image,
                    apple_care=adapter["apple_care_plus"],
                    condition="U" if entity.unused else "S",
                )
            )

            self.session.commit()
            spider.logger.info(
                f"[{type(self).__name__}][{item['id']}] end processing item"
            )
            return item
        except Exception as e:
            self.session.rollback()
            raise DropAndMarkItem(
                f"[PersisPipeline] Can't update item: {adapter['id']}, {e}"
            )


class DealAlertPipeline:
    name = "DealAlertPipeline"

    def __init__(self):
        self.slack_bot = LabelingSlackBot()
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def get_entity(self, url: str) -> Deal:
        entity = self.session.query(Deal).filter(Deal.url == url).first()
        return entity

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )

        entity = self.get_entity(adapter["url"])

        model = adapter["model"]
        source = entity.source

        if model == "IPADMINI" and adapter["generation"] == 5:
            self.slack_bot.post_hotdeal_message(
                console_url=NEW_CONSOLE_URL % entity.id,
                source=source,
                msg="아이패드 미니 5세대, 한번 봐주세요",
            )

        return item
