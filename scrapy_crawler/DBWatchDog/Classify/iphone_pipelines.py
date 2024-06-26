import re

from itemadapter import ItemAdapter
from langchain import LLMChain

from scrapy_crawler.common.chatgpt.CallBacks import CloudWatchCallbackHandler
from scrapy_crawler.common.chatgpt.chains import (
    iphone_generation_chain,
    iphone_model_chain,
    iphone_storage_chain,
)
from scrapy_crawler.common.db.models import ItemIphone
from scrapy_crawler.common.utils.custom_exceptions import DropUnsupportedIphoneItem
from scrapy_crawler.DBWatchDog.items import IphoneItem

cloudwatchCallbackHandler = CloudWatchCallbackHandler()


class GenerationClassifierPipeline:
    name = "GenerationClassifierPipeline"

    def __init__(self):
        self.chain: LLMChain = iphone_generation_chain
        self.generations = [12, 13, 14]

    def process_item(self, item, spider):
        if not isinstance(item, IphoneItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )
        try:
            predict = (
                self.chain.run(
                    title=adapter["title"],
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

            generation = int(re.findall(r"\d+", predict)[0])
            if generation not in self.generations:
                raise DropUnsupportedIphoneItem(
                    f"GenerationClassifierPipeline: {generation} not in {self.generations}"
                )

            item["generation"] = generation
            return item

        except Exception as e:
            raise DropUnsupportedIphoneItem(f"ModelClassifierPipeline: {e}")


class ModelClassifierPipeline:
    name = "ModelClassifierPipeline"

    def __init__(self):
        self.chain: LLMChain = iphone_model_chain
        self.models = ["DEFAULT", "MINI", "PLUS", "PRO", "PROMAX"]

    def process_item(self, item, spider):
        if not isinstance(item, IphoneItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )
        try:
            predict = (
                self.chain.run(
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

            model = re.findall(r"MODEL=(\S+)", predict)[0]

            if model not in self.models:
                raise DropUnsupportedIphoneItem(
                    f"ModelClassifierPipeline: {model} not in {self.models}"
                )

            item["model"] = model
            return item

        except Exception as e:
            raise DropUnsupportedIphoneItem(f"ModelClassifierPipeline: {e}")


class StorageClassifierPipeline:
    name = "StorageClassifierPipeline"

    def __init__(self):
        self.storage_chain: LLMChain = iphone_storage_chain
        self.storage_map = {
            "12": {
                "DEFAULT": 64,
                "MINI": 64,
                "PRO": 128,
                "PROMAX": 128,
            },
            "13": {
                "DEFAULT": 128,
                "MINI": 128,
                "PRO": 128,
                "PROMAX": 128,
            },
            "14": {
                "DEFAULT": 128,
                "PLUS": 128,
                "PRO": 128,
                "PROMAX": 128,
            },
        }

    def process_item(self, item, spider):
        if not isinstance(item, IphoneItem):
            return item

        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )
        try:
            generation = adapter["generation"]
            model = adapter["model"]

            if self.storage_map.get(str(generation)).get(model) is None:
                raise DropUnsupportedIphoneItem(
                    f"StorageClassifierPipeline: {generation} {model} not in {self.storage_map}"
                )

            default_storage = self.storage_map.get(str(generation)).get(model)
            predict = (
                self.storage_chain.run(
                    title=adapter["title"],
                    content=adapter["content"],
                    default_storage=default_storage,
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

            storage = re.findall(r"STORAGE=(\d+)", predict)[0]
            storage += "TB" if storage < "10" else "GB"
            item["ssd"] = storage
            return item

        except Exception as e:
            raise DropUnsupportedIphoneItem(f"ModelClassifierPipeline: {e}")


class IphoneClassifyPipeline:
    name = "IphoneClassifyPipeline"

    def __init__(self):
        self.session = None
        self.model_id_map = {
            "12": 12,
            "13": 13,
            "14": 14,
        }

    def process_item(self, item, spider):
        if not isinstance(item, IphoneItem):
            return item

        self.session = spider.session
        adapter = ItemAdapter(item)
        spider.logger.info(
            f"[{type(self).__name__}][{adapter['id']}] start processing item"
        )

        model_id = self.model_id_map.get(str(adapter["generation"]))
        storage = item["ssd"]
        suffix = item["model"]

        try:
            entity: ItemIphone = (
                self.session.query(ItemIphone)
                .filter(ItemIphone.model == model_id)
                .filter(ItemIphone.ssd == storage)
                .filter(ItemIphone.model_suffix == suffix)
                .first()
            )
        except Exception as e:
            raise DropUnsupportedIphoneItem(f"IphoneClassifyPipeline: {e}")

        if entity is None:
            raise DropUnsupportedIphoneItem(
                f"IphoneClassifyPipeline: {adapter['id']} not found"
            )

        item["item_id"] = entity.id
        return item
