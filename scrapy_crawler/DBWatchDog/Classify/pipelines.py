import logging
import re
from datetime import datetime
from typing import Optional

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem, NotSupported
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
from scrapy_crawler.common.utils.constants import CONSOLE_URL
from scrapy_crawler.DBWatchDog.items import IpadItem, MacbookItem

log_group_name = "scrapy-chatgpt"


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
                CloudWatchCallbackHandler(
                    log_group_name=log_group_name,
                    log_stream_name=adapter["id"],
                    function_name=type(self).__name__,
                )
            ],
        ).upper()

        result: re.Match[bytes] | None = re.search(r"IPAD|MAC", raw_result)
        try:
            category = result.group().upper()

            return IpadItem(**adapter) if category == "IPAD" else MacbookItem(**adapter)

        except Exception as e:
            raise DropItem(f"CategoryClassifierPipeline: {e}")


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
                    CloudWatchCallbackHandler(
                        log_group_name=log_group_name,
                        log_stream_name=adapter["id"],
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
        apple_care = False
        title = adapter["title"]
        content = adapter["content"]

        regex = re.compile(r"애플케어플러스|애케플|애캐플|케어|캐어|CARE")

        if regex.search(title + content) is not None:
            try:
                predict = self.apple_care_plus_chain.run(
                    title=title,
                    content=content,
                    callbacks=[
                        CloudWatchCallbackHandler(
                            log_group_name=log_group_name,
                            log_stream_name=adapter["id"],
                            function_name=type(self).__name__,
                        )
                    ],
                )

                apple_care = "TRUE" in predict.upper()
            except Exception:
                apple_care = False

        adapter["apple_care_plus"] = apple_care

        return item


class HotDealClassifierPipeline:
    name = "HotDealClassifierPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def get_average_price(self, item) -> Optional[ViewTrade]:
        try:
            type = "P" if isinstance(item, IpadItem) else "M"
            entity = (
                self.session.query(ViewTrade)
                .filter(ViewTrade.id == item["item_id"])
                .filter(ViewTrade.source == item["source"])
                .filter(ViewTrade.type == type)
                .filter(ViewTrade.unused == item["unused"])
                .filter(
                    ViewTrade.date == datetime.date(datetime.now()).strftime("%Y-%m-%d")
                )
                .first()
            )
            return entity
        except Exception:
            self.session.rollback()
            return None

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )
        priceInfo = self.get_average_price(item)

        if priceInfo is None or priceInfo.average is None or priceInfo.price_20 is None:
            return item
        elif not (priceInfo.average * 0.8 <= adapter["price"] <= priceInfo.price_20):
            raise DropItem(f"HotDealClassifierPipeline: Not hot deal {adapter['id']}")

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
            item_type = "P" if isinstance(item, IpadItem) else "M"
            item_id = adapter["item_id"]
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
            raise DropItem(f"[{type(self).__name__}][{item['id']}] {e}")


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

    def is_macbook_air_15inch(self, item) -> bool:
        return item["model"] == "AIR" and item["screen_size"] == 15

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{item['id']}] start processing item"
        )

        if self.has_multiple_generation(item) or self.is_macbook_air_15inch(item):
            self.slack_bot.post_hotdeal_message(
                console_url=CONSOLE_URL % adapter["id"], source=adapter["source"]
            )

            raise NotSupported("Stop processing item")

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
        item_type = "P" if isinstance(item, IpadItem) else "M"
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
            raise DropItem(f"[PersisPipeline] Can't update item: {adapter['id']}, {e}")


# For Deal table
# class LabelingAlertPipeline:
#     name = "LabelingAlertPipeline"
#
#     def __init__(self):
#         self.slack_bot = LabelingSlackBot()
#         self.session = None
#
#     def open_spider(self, spider):
#         self.session = sessionmaker(bind=get_engine())()
#
#     def close_spider(self, spider):
#         self.session.close()
#
#     def get_entity(self, url: str) -> Deal:
#         entity = self.session.query(Deal).filter(Deal.url == url).first()
#         return entity
#
#     def process_item(self, item, spider):
#         adapter = ItemAdapter(item)
#         spider.logger.info(
#             f"[{type(self).__name__}][{item['id']}] start processing item"
#         )
#
#         entity = self.get_entity(adapter["url"])
#
#         model = adapter["model"]
#         source = entity.source
#
#         if (
#             model == "IPADPRO"
#             or source != "중고나라"
#             or re.findall("미개봉|새제품", adapter["title"] + adapter["content"])
#         ):
#             self.slack_bot.post_hotdeal_message(
#                 console_url=f"https://dev.macguider.io/deals/report/{entity.id}",
#                 source=source,
#             )
#
#         return item
