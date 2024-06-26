import logging
import re
from typing import Optional

from itemadapter import ItemAdapter
from langchain import LLMChain

from scrapy_crawler.common.chatgpt.CallBacks import CloudWatchCallbackHandler
from scrapy_crawler.common.chatgpt.chains import (
    macbook_air_13_chain,
    macbook_chain,
    macbook_pro_13_chain,
    macbook_pro_14_chain,
    macbook_pro_16_chain,
    macbook_system_chain,
    macmini_chain,
)
from scrapy_crawler.common.db.models import ItemMacbook
from scrapy_crawler.common.utils.custom_exceptions import DropUnsupportedMacbookItem
from scrapy_crawler.DBWatchDog.items import MacbookItem

cloudwatchCallbackHandler = CloudWatchCallbackHandler()


class ModelClassifierPipeline:
    name = "ModelClassifierPipeline"

    def __init__(self):
        self.macbook_chain: LLMChain = macbook_chain

    def process_item(self, item, spider):
        if not isinstance(item, MacbookItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )
        try:
            predict = self.macbook_chain.run(
                title=adapter["title"],
                content=adapter["content"],
                callbacks=[
                    cloudwatchCallbackHandler.set_meta_data(
                        log_stream_name=str(adapter["id"]),
                        function_name=type(self).__name__,
                    )
                ],
            ).upper()

            model = re.search(r"AIR|PRO|MINI", predict).group()
            if model == "MINI":
                screen_size = -1
            else:
                screen_size = int(re.findall("13|14|15|16", predict)[0])

            adapter["model"] = model
            adapter["screen_size"] = screen_size

            return item

        except Exception as e:
            raise DropUnsupportedMacbookItem(f"ModelClassifierPipeline: {e}")


class ChipClassifierPipeline:
    name = "ChipClassifierPipeline"

    def __init__(self):
        self.chain_map = {
            "AIR": dict(
                {
                    13: macbook_air_13_chain,
                }
            ),
            "PRO": dict(
                {
                    13: macbook_pro_13_chain,
                    14: macbook_pro_14_chain,
                    16: macbook_pro_16_chain,
                }
            ),
            "MINI": dict(
                {
                    -1: macmini_chain,
                }
            ),
        }

    def process_item(self, item, spider):
        if not isinstance(item, MacbookItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        # Macbook Air 15 inch
        if adapter["model"] == "AIR" and adapter["screen_size"] == 15:
            adapter["chip"] = "M2"
            adapter["cpu_core"] = 8
            adapter["gpu_core"] = 10
            return item

        try:
            chain: LLMChain = self.chain_map[adapter["model"]][adapter["screen_size"]]
            predict = (
                chain.run(
                    title=adapter["title"],
                    content=adapter["content"],
                    callbacks=[
                        cloudwatchCallbackHandler.set_meta_data(
                            log_stream_name=str(adapter["id"]),
                            function_name=type(self).__name__,
                        )
                    ],
                )
                .upper()
                .replace(" ", "")
            )

            adapter["chip"] = re.findall(r"CHIP=(\w+)", predict)[0]
            adapter["cpu_core"] = int(re.findall(r"CPU_CORE=(\d+)", predict)[0])
            adapter["gpu_core"] = int(re.findall(r"GPU_CORE=(\d+)", predict)[0])

            return item

        except Exception as e:
            raise DropUnsupportedMacbookItem(f"ChipClassifierPipeline: {e}")


class SystemClassifierPipeline:
    name = "SystemClassifierPipeline"

    def __init__(self):
        self.macbook_chain = macbook_system_chain

    def process_item(self, item, spider):
        if not isinstance(item, MacbookItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        chip = adapter["chip"]
        title = adapter["title"]
        content = adapter["content"]

        default_ram = 8
        default_ssd = 256

        if "PRO" in chip:
            default_ram = 16
            default_ssd = 512
        elif "MAX" in chip:
            default_ram = 32
            default_ssd = 1024

        try:
            predict = (
                self.macbook_chain.run(
                    title=title,
                    content=content,
                    default_ram=default_ram,
                    default_ssd=default_ssd,
                    callbacks=[
                        cloudwatchCallbackHandler.set_meta_data(
                            log_stream_name=str(adapter["id"]),
                            function_name=type(self).__name__,
                        )
                    ],
                )
                .upper()
                .replace(" ", "")
            )

            adapter["ram"] = re.findall(r"RAM=(\d+)", predict)[0]
            adapter["ssd"] = re.findall(r"SSD=(\d+)", predict)[0]

            if adapter["ssd"] <= "10":
                adapter["ssd"] += "TB"
            else:
                adapter["ssd"] += "GB"

            return item
        except Exception as e:
            raise DropUnsupportedMacbookItem(f"SystemClassifierPipeline: {e}")


class MacbookClassifyPipeline:
    name = "MacbookClassifyPipeline"

    def __init__(self):
        self.session = None
        self.map = {
            "MINI": {-1: 1},
            "AIR": {
                13: 2,
                15: 11,
            },
            "PRO": {
                13: 3,
                14: 4,
                16: 5,
            },
        }

    def get_item_id(self, adapter) -> Optional[ItemMacbook]:
        try:
            model_id = self.map[adapter["model"]][adapter["screen_size"]]
            item_id = (
                self.session.query(ItemMacbook)
                .filter(
                    ItemMacbook.model == model_id,
                    ItemMacbook.chip == adapter["chip"],
                    ItemMacbook.cpu_core == adapter["cpu_core"],
                    ItemMacbook.gpu_core == adapter["gpu_core"],
                    ItemMacbook.ssd == adapter["ssd"],
                    ItemMacbook.ram == adapter["ram"],
                )
                .first()
            )
            return item_id
        except Exception as e:
            logging.error(f"get_item_id: {e}")
            self.session.rollback()
            return None

    def process_item(self, item, spider):
        if not isinstance(item, MacbookItem):
            return item

        self.session = spider.session
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )
        item_id = self.get_item_id(adapter)
        if item_id is None:
            raise DropUnsupportedMacbookItem(
                f"Item not found in database for {adapter['id']}"
            )

        adapter["item_id"] = item_id.id

        return item
