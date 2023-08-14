import logging

import watchtower
from scrapy import Spider
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import RawUsedItem, get_engine
from scrapy_crawler.common.utils import save_image_from_url
from scrapy_crawler.Daangn.items import ArticleItem


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


class PersistPipeline:
    name = "PersistPipeline"

    def __init__(self):
        self.session = sessionmaker(bind=get_engine())()

    def process_item(self, item, spider):
        if not isinstance(item, ArticleItem):
            return item

        spider.logger.info(f"[{type(self).__name__}][{item['id']}] start process_item")
        try:
            self.session.query(RawUsedItem).filter(RawUsedItem.id == item["id"]).update(
                {
                    RawUsedItem.title: item["title"],
                    RawUsedItem.content: item["content"],
                    RawUsedItem.writer: item["writer"],
                    RawUsedItem.price: item["price"],
                    RawUsedItem.img_url: item["img_url"],
                    RawUsedItem.image: save_image_from_url(item["img_url"]).getvalue(),
                }
            )
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"[{type(self).__name__}] {e}")

        return item
