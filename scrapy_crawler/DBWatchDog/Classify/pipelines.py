import logging
import re
from datetime import datetime
from typing import Optional

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import true
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
from scrapy_crawler.DBWatchDog.items import IpadItem, MacbookItem

log_group_name = "scrapy-chatgpt"


class MarkAsClassifiedPipeline:
    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.warning(f"[{type(self).__name__}] start processing item: {item['id']}")

        try:
            self.session.query(RawUsedItem).filter(
                RawUsedItem.url == adapter["url"]
            ).update({RawUsedItem.classified: true()})
            self.session.commit()
            return item

        except Exception as e:
            logging.error(e)
            self.session.rollback()
            raise DropItem(f"MarkAsClassifiedPipeline: {e}")


class CategoryClassifierPipeline:
    def __init__(self):
        self.chain = category_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.warning(
            f"[{type(self).__name__}] start processing item: {adapter['id']}"
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

        result: re.Match[bytes] | None = re.search(r"IPAD|MACBOOK", raw_result)

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
        logging.warning(
            f"[{type(self).__name__}] start processing item: {adapter['id']}"
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
        logging.warning(
            f"[{type(self).__name__}] start processing item: {adapter['id']}"
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
        except Exception as e:
            logging.error(e)
            self.session.rollback()
            return None

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.warning(
            f"[{type(self).__name__}] start processing item: {adapter['id']}"
        )
        priceInfo = self.get_average_price(item)

        if priceInfo is None:
            raise DropItem(
                f"HotDealClassifierPipeline: Can't find average price {adapter['id']}"
            )

        if priceInfo.average is None:
            raise DropItem(
                f"HotDealClassifierPipeline: Don't have trade data {adapter['id']}, {adapter}"
            )

        if not (priceInfo.average * 0.8 <= adapter["price"] <= priceInfo.price_20):
            raise DropItem(f"HotDealClassifierPipeline: Not hot deal {adapter['id']}")

        return item


class LabelingAlertPipeline:
    name = "LabelingAlertPipeline"

    def __init__(self):
        self.slack_bot = LabelingSlackBot()
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def get_entity(self, id: int) -> Optional[RawUsedItem]:
        try:
            entity = (
                self.session.query(RawUsedItem).filter(RawUsedItem.id == id).first()
            )
            return entity
        except Exception as e:
            logging.error(e)
            return None

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.warning(
            f"[{type(self).__name__}] start processing item: {adapter['id']}"
        )
        entity = self.get_entity(adapter["id"])
        if entity is None:
            raise DropItem(f"LabelingAlertPipeline: Can't find entity {adapter['id']}")

        model = adapter["model"]
        source = entity.source

        if model == "IPADPRO" or source != "중고나라":
            self.slack_bot.post_hotdeal_message(
                console_url=f"https://dev.macguider.io/deals/admin/{adapter['id']}",
                source=source,
            )

            raise DropItem(
                f"LabelingAlertPipeline: Need manual labeling {adapter['id']}"
            )

        return item


class PersistPipeline:
    name = "PersistPipeline"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.warning(
            f"[{type(self).__name__}] start processing item: {adapter['id']}"
        )
        item_type = "P" if isinstance(item, IpadItem) else "M"
        try:
            # Update RawUsedItem
            self.session.query(RawUsedItem).filter(
                RawUsedItem.id == adapter["id"]
            ).update(
                {
                    RawUsedItem.type: item_type,
                    RawUsedItem.item_id: adapter["item_id"],
                    RawUsedItem.unused: adapter["unused"],
                }
            )

            # Get RawUsedItem
            entity: RawUsedItem = (
                self.session.query(RawUsedItem)
                .filter(RawUsedItem.id == adapter["id"])
                .first()
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
                    apple_care=adapter["apple_care_plus"],
                )
            )

            self.session.commit()
            logging.warning(f"[PersisPipeline] update item: {adapter['id']}")
            return item
        except Exception as e:
            logging.error(e)
            self.session.rollback()
            raise DropItem(f"[PersisPipeline] Can't update item: {adapter['id']}, {e}")
