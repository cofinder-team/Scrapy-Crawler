import logging
import re
from typing import Optional

from itemadapter import ItemAdapter
from langchain import LLMChain
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.chatgpt.CallBacks import CloudWatchCallbackHandler
from scrapy_crawler.common.chatgpt.chains import (
    ipad_cellular_chain,
    ipad_chain,
    ipad_gen_chain,
    ipad_system_chain,
)
from scrapy_crawler.common.db import get_engine
from scrapy_crawler.common.db.models import ItemIpad
from scrapy_crawler.DBWatchDog.items import IpadItem

log_group_name = "scrapy-chatgpt"


class ModelClassifierPipeline:
    name = "ModelClassifierPipeline"

    def __init__(self):
        self.ipad_chain: LLMChain = ipad_chain
        self.screen_size_map = {
            "MINI": 8.3,
            "IPAD": 12.9,
        }

    def process_item(self, item, spider):
        if not isinstance(item, IpadItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        predict = (
            self.ipad_chain.run(
                title=adapter["title"],
                content=adapter["content"],
                callbacks=[
                    CloudWatchCallbackHandler(
                        log_group_name=log_group_name,
                        log_stream_name=adapter["id"],
                        function_name=type(self).__name__,
                    )
                ],
            )
            .upper()
            .replace(" ", "")
        )

        try:
            model = re.search(r"IPADPRO|IPADMINI|IPADAIR|IPAD", predict).group()
            screen_size = float(
                re.search(r"8.3|10.2|10.9|10|11|12.9|12", predict).group()
            )

            adapter["model"] = model
            adapter["screen_size"] = screen_size

            if model in self.screen_size_map:
                adapter["screen_size"] = self.screen_size_map.get(model, screen_size)

            return item
        except Exception as e:
            raise DropItem(f"ModelClassifierPipeline: {e}")


class GenerationClassifierPipeline:
    name = "GenerationClassifierPipeline"

    def __init__(self):
        self.gen_chain: LLMChain = ipad_gen_chain
        self.generation_map = {
            "IPADPRO": dict(
                {
                    11: [2, 3, 4],
                    12.9: [4, 5, 6],
                }
            ),
            "IPADAIR": dict(
                {
                    10.9: [4, 5],
                }
            ),
            "IPAD": dict(
                {
                    12.9: [8, 9, 10],
                }
            ),
            "IPADMINI": dict(
                {
                    8.3: [6],
                }
            ),
        }

    def process_item(self, item, spider):
        if not isinstance(item, IpadItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )
        try:
            predict = self.gen_chain.run(
                title=adapter["title"],
                content=adapter["content"],
                callbacks=[
                    CloudWatchCallbackHandler(
                        log_group_name=log_group_name,
                        log_stream_name=adapter["id"],
                        function_name=type(self).__name__,
                    )
                ],
            ).upper()

            generation = int(re.search(r"GENERATION=(\d+)", predict).group(1))
            if (
                generation
                in self.generation_map[adapter["model"]][adapter["screen_size"]]
            ):
                adapter["generation"] = generation

            return item
        except Exception as e:
            raise DropItem(f"GenerationClassifierPipeline: {e}")


class StorageClassifierPipeline:
    name = "StorageClassifierPipeline"

    def __init__(self):
        self.ipad_chain = ipad_system_chain
        self.storage_map = {
            "IPADAIR": dict(
                {
                    4: 64,
                    5: 64,
                }
            ),
            "IPAD": dict(
                {
                    8: 32,
                    9: 64,
                    10: 64,
                }
            ),
            "IPADPRO": dict(
                {
                    2: 128,
                    3: 128,
                    4: 128,
                    5: 128,
                    6: 128,
                }
            ),
            "IPADMINI": dict(
                {
                    6: 64,
                }
            ),
        }

    def process_item(self, item, spider):
        if not isinstance(item, IpadItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        title = adapter["title"]
        content = adapter["content"]
        generation = adapter["generation"]
        default_storage = self.storage_map[adapter["model"]][generation]

        try:
            predict = (
                self.ipad_chain.run(
                    title=title,
                    content=content,
                    default_ssd=default_storage,
                    callbacks=[
                        CloudWatchCallbackHandler(
                            log_group_name=log_group_name,
                            log_stream_name=adapter["id"],
                            function_name=type(self).__name__,
                        )
                    ],
                )
                .upper()
                .replace(" ", "")
            )

            adapter["ssd"] = re.findall(r"SSD=(\S+)", predict)[0]

            if adapter["ssd"] == "1024GB" or adapter["ssd"] == "1024":
                adapter["ssd"] = "1TB"
            elif adapter["ssd"] == "500GB":
                adapter["ssd"] = "512GB"

            return item
        except Exception as e:
            raise DropItem(f"StorageClassifierPipeline: {e}")


class CellularClassifierPipeline:
    name = "CellularClassifierPipeline"

    def __init__(self):
        self.ipad_cellular_chain = ipad_cellular_chain

    def process_item(self, item, spider):
        if not isinstance(item, IpadItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        title = adapter["title"].upper()
        content = adapter["content"].upper()

        regex = re.compile(r"셀룰|LTE|Cellular|")

        if regex.search(title + content) is None:
            adapter["cellular"] = False
        else:
            try:
                predict = self.ipad_cellular_chain.run(
                    title=title,
                    content=content,
                    callbacks=[
                        CloudWatchCallbackHandler(
                            log_group_name=log_group_name,
                            log_stream_name=adapter["id"],
                            function_name=type(self).__name__,
                        )
                    ],
                ).upper()

                adapter["cellular"] = re.findall(r"(\w+)", predict)[0] == "TRUE"
            except Exception as e:
                spider.logger.error(
                    f"[{type(self).__name__}][{adapter['id']}] error: {e}"
                )
                adapter["cellular"] = False

        return item


class IpadClassifyPipeline:
    name = "IpadClassifyPipeline"

    def __init__(self):
        self.session = None
        self.map = {
            "IPADMINI": {8.3: 6},
            "IPADAIR": {
                10.9: 7,
            },
            "IPAD": {
                12.9: 8,
            },
            "IPADPRO": {
                11: 9,
                12.9: 10,
            },
        }

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def get_item_id(self, adapter) -> Optional[ItemIpad]:
        try:
            model_id = self.map[adapter["model"]][adapter["screen_size"]]
            item_id = (
                self.session.query(ItemIpad)
                .filter(
                    ItemIpad.model == model_id,
                    ItemIpad.generation == adapter["generation"],
                    ItemIpad.ssd == adapter["ssd"],
                    ItemIpad.cellular == adapter["cellular"],
                )
                .first()
            )

            return item_id
        except Exception as e:
            logging.error(f"[{type(self).__name__}] {e}")
            self.session.rollback()
            return None

    def process_item(self, item, spider):
        if not isinstance(item, IpadItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        ipadItem = self.get_item_id(adapter)
        if ipadItem is None:
            raise DropItem(f"Item not found in database : {adapter['id']}")
        adapter["item_id"] = ipadItem.id

        return item
