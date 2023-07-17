from itemadapter import ItemAdapter
import re
import logging
from scrapy.exceptions import DropItem

from scrapy_crawler.util.slack.SlackBots import LabelingSlackBot
from scrapy_crawler.util.chatgpt.chains import *


class CategoryClassifierPipeline:

    def __init__(self):
        self.chain = category_chain
        self.category_map = {
            "MACBOOK": "M",
            "IPAD": "P",
        }

    def init_pipelines(self, item: ItemAdapter):
        if item["type"] == "M":
            item["pipelines"] = [
                MacbookModelClassifierPipeline.__name__,
                ChipClassifierPipeline.__name__,
                MacbookRamSSDClassifierPipeline.__name__,
                UnusedClassifierPipeline.__name__,
                SlackAlertPipeline.__name__,
            ]
        elif item["type"] == "P":
            item["pipelines"] = [
                IpadModelClassifierPipeline.__name__,
                IpadGenerationClassifierPipeline.__name__,
                IpadStorageClassifierPipeline.__name__,
                IpadCellularClassifierPipeline.__name__,
                UnusedClassifierPipeline.__name__,
                SlackAlertPipeline.__name__,
            ]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        raw_result: str = self.chain.run(title=adapter["title"]).upper()
        result: re.Match[bytes] | None = re.search(r"IPAD|MACBOOK|ETC", raw_result)

        try:
            category = result.group().upper()
            adapter["type"] = self.category_map[category]

        except IndexError or KeyError:
            raise DropItem("Not MacBook or iPad")

        if adapter["type"] != "P":
            raise DropItem("Not iPad")

        self.init_pipelines(adapter)
        return item


class MacbookModelClassifierPipeline:
    name = "MacbookModelClassifierPipeline"

    def __init__(self):
        self.macbook_chain: LLMChain = macbook_chain
        self.screen_size_map = {
            "AIR": 13,
            "MINI": -1,
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        try:
            predict = self.macbook_chain.run(title=adapter["title"], content=adapter["content"]).upper()
            model = re.search(r"AIR|PRO|MINI", predict).group()
            screen_size = int(re.findall("13|14|16", predict)[0])
        except IndexError:
            model = "UNKNOWN"
            screen_size = -1

        adapter["model"] = model
        adapter["screen_size"] = screen_size

        # Manually set screen size
        if model in self.screen_size_map:
            adapter["screen_size"] = self.screen_size_map.get(model, screen_size)

        return item


class ChipClassifierPipeline:
    name = "ChipClassifierPipeline"

    def __init__(self):
        self.chain_map = {
            "AIR": dict({
                13: macbook_air_13_chain,
            }),
            "PRO": dict({
                13: macbook_pro_13_chain,
                14: macbook_pro_14_chain,
                16: macbook_pro_16_chain,
            }),
            "MINI": dict({
                -1: macmini_chain,
            })
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        try:
            chain: LLMChain = self.chain_map[adapter["model"]][adapter["screen_size"]]
            predict = chain.run(title=adapter["title"], content=adapter["content"]).upper().replace(" ", "")
            adapter["chip"] = re.findall(r"CHIP=(\w+)", predict)[0]
            adapter["cpu_core"] = int(re.findall(r"CPU_CORE=(\d+)", predict)[0])
            adapter["gpu_core"] = int(re.findall(r"GPU_CORE=(\d+)", predict)[0])

        except Exception as e:
            raise DropItem(f"[{self.name}]Unknown error : {e}")

        return item


class MacbookRamSSDClassifierPipeline:
    name = "MacbookRamSSDClassifierPipeline"

    def __init__(self):
        self.macbook_chain = macbook_system_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if type(self).__name__ not in adapter["pipelines"]:
            return item

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
            predict = self.macbook_chain.run(title=title, content=content, default_ram=default_ram,
                                             default_ssd=default_ssd).upper().replace(" ", "")

            adapter["ram"] = re.findall(r'RAM=(\d+)GB', predict)[0]
            adapter["ssd"] = re.findall(r'SSD=(\d+)', predict)[0]
            if adapter["ssd"] == "1024GB" or adapter["ssd"] == "1024":
                adapter["ssd"] = "1TB"

        except Exception as e:
            raise DropItem(f"[{self.name}]Unknown error : {e}")

        return item


class IpadModelClassifierPipeline:
    name = "IpadModelClassifierPipeline"

    def __init__(self):
        self.ipad_chain: LLMChain = ipad_chain
        self.screen_size_map = {
            "MINI": 8.3,
            "IPAD": 10.9,
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        predict = self.ipad_chain.run(title=adapter["title"], content=adapter["content"]).upper().replace(" ", "")
        try:
            model = re.search(r"IPADPRO|IPADMINI|IPADAIR|IPAD", predict).group()
            screen_size = float(re.search(r"8.3|10.2|10.9|10|11|12.9|12", predict).group())
        except Exception as e:
            raise DropItem(f"[{self.name}]Unknown error : {e}, {predict}")

        adapter["model"] = model
        adapter["screen_size"] = screen_size

        # Manually set screen size
        if model in self.screen_size_map:
            adapter["screen_size"] = self.screen_size_map.get(model, screen_size)

        return item


class IpadGenerationClassifierPipeline:
    name = "IpadGenerationClassifierPipeline"

    def __init__(self):
        self.gen_chain: LLMChain = ipad_gen_chain
        self.generation_map = {
            "IPADPRO": dict({
                11: [2, 3, 4],
                12.9: [4, 5, 6],
            }),
            "IPADAIR": dict({
                10.9: [4, 5],
            }),
            "IPAD": dict({
                10.9: [8, 9, 10],
            }),
            "IPADMINI": dict({
                8.3: [6],
            })
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        try:
            predict = self.gen_chain.run(title=adapter["title"], content=adapter["content"]).upper()
            generation = int(re.search(r"GENERATION=(\d+)", predict).group(1))
            if generation in self.generation_map[adapter["model"]][adapter["screen_size"]]:
                adapter["generation"] = generation
            else:
                raise DropItem(f"[{self.name}]Unknown generation : {generation}")

        except Exception as e:
            raise DropItem(f"[{self.name}]Unknown error : {e}")

        return item


class IpadStorageClassifierPipeline:
    name = "IpadStorageClassifierPipeline"

    def __init__(self):
        self.ipad_chain = ipad_system_chain
        self.storage_map = {
            "IPADAIR": dict({
                4: 64,
                5: 64,
            }),
            "IPAD": dict({
                8: 32,
                9: 64,
                10: 64,
            }),
            "IPADPRO": dict({
                2: 128,
                3: 128,
                4: 128,
                5: 128,
                6: 128,
            }),
            "IPADMINI": dict({
                6: 64,
            })

        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        title = adapter["title"]
        content = adapter["content"]
        generation = adapter["generation"]
        default_storage = self.storage_map[adapter["model"]][generation]

        try:
            predict = self.ipad_chain.run(title=title, content=content, default_ssd=default_storage).upper().replace(
                " ", "")
            adapter["ssd"] = re.findall(r'SSD=(\d+)', predict)[0]
        except Exception as e:
            raise DropItem(f"[{self.name}]Unknown error : {e}")

        return item


class IpadCellularClassifierPipeline:
    def __init__(self):
        self.ipad_cellular_chain = ipad_cellular_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        title = adapter["title"].upper()
        content = adapter["content"].upper()

        regex = re.compile(r'셀룰|LTE|Cellular|')

        if regex.search(title + content) is None:
            adapter["cellular"] = False
        else:
            try:
                predict = self.ipad_cellular_chain.run(title=title, content=content).upper()
                adapter["cellular"] = re.findall(r'(\w+)', predict)[0] == "TRUE"
            except Exception as e:
                adapter["cellular"] = False

        return item


class UnusedClassifierPipeline:
    def __init__(self):
        self.unused_chain = unused_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        title = adapter["title"]
        content = adapter["content"]

        regex = re.compile(r'미개봉')
        adapter["unused"] = regex.search(title + content) is not None
        return item


class AppleCarePlusClassifierPipeline:
    def __init__(self):
        self.apple_care_plus_chain = apple_care_plus_chain

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item

        title = adapter["title"]
        content = adapter["content"]

        regex = re.compile(r'애플케어플러스|애케플|애캐플|케어|캐어|CARE')

        if regex.search(title + content) is not None:
            try:
                predict = self.apple_care_plus_chain.run(title=title, content=content).upper()
                adapter["apple_care_plus"] = re.findall(r'(\w+)', predict)[0] == "TRUE"
            except Exception as e:
                adapter["apple_care_plus"] = False
                return

        return item


class SlackAlertPipeline:
    def __init__(self):
        self.slack_bot = LabelingSlackBot()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if adapter["type"] == "M":
            self.slack_bot.post_macbook_message(
                url=adapter["url"],
                title=adapter["title"],
                source=adapter["source"],
                model=adapter["model"],
                screen_size=adapter["screen_size"],
                chip=adapter["chip"],
                cpu=",".join([str(adapter["cpu_core"]), str(adapter["gpu_core"])]),
                ram=adapter["ram"],
                ssd=adapter["ssd"],
                unused=adapter["unused"],
                apple_care_plus=False,
                id=adapter["id"],
            )
        else:
            self.slack_bot.post_ipad_message(
                url=adapter["url"],
                source=adapter["source"],
                title=adapter["title"],
                model=adapter["model"],
                screen_size=adapter["screen_size"],
                gen=adapter["generation"],
                cellular=adapter["cellular"],
                ssd=adapter["ssd"],
                unused=adapter["unused"],
                apple_care_plus=False,
                id=adapter["id"],
            )
        return item
