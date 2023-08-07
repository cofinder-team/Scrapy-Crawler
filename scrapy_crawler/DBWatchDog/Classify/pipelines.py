import datetime
import logging
import re

import watchtower
from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem, NotSupported
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
from scrapy_crawler.common.utils.constants import CONSOLE_URL
from scrapy_crawler.DBWatchDog.items import IpadItem, MacbookItem

log_group_name = "scrapy-chatgpt"


class InitCloudwatchLogger:
    name = "InitCloudwatchLogger"

    def process_item(self, item, spider: Spider):
        logger = logging.getLogger(spider.name)
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        console_handler = logging.StreamHandler()
        cw_handler = watchtower.CloudWatchLogHandler(
            log_group="scrapy-chatgpt",
            stream_name=f"{item['id']}",
        )

        logger.addHandler(console_handler)
        logger.addHandler(cw_handler)

        return item


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

    def is_abnormal_price(self, item: MacbookItem | IpadItem) -> bool:
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

        if self.has_multiple_generation(item):
            self.slack_bot.post_hotdeal_message(
                console_url=CONSOLE_URL % adapter["id"],
                source=adapter["source"],
                msg="세대수 검증(여러 세대 존재)",
            )

            raise NotSupported("Stop processing item")

        if self.is_abnormal_price(item):
            self.slack_bot.post_hotdeal_message(
                console_url=CONSOLE_URL % adapter["id"],
                source=adapter["source"],
                msg="가격/모델 검증(가격 비정상)",
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
