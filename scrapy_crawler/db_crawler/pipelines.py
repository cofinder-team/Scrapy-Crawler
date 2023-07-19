from itemadapter import ItemAdapter
import re
import logging

from scrapy.exceptions import DropItem

from scrapy_crawler.db_crawler.items import DBMacbookItem, DBIpadItem
from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy_crawler.util.exceptions import DropAndAlert
from scrapy_crawler.util.slack.SlackBots import LabelingSlackBot
from scrapy_crawler.util.chatgpt.chains import *


class CategoryClassifierPipeline:

    def __init__(self):
        self.chain = category_chain
        self.category_map = {
            "MACBOOK": "M",
            "IPAD": "P",
        }

        self.pipeline_map = {
            "M": [
                MacbookModelClassifierPipeline.__name__,
                ChipClassifierPipeline.__name__,
                MacbookRamSSDClassifierPipeline.__name__,
                UnusedClassifierPipeline.__name__,
                DBExportPipeline.__name__,
                SlackAlertPipeline.__name__,
            ],
            "P": [
                IpadModelClassifierPipeline.__name__,
                IpadGenerationClassifierPipeline.__name__,
                IpadStorageClassifierPipeline.__name__,
                IpadCellularClassifierPipeline.__name__,
                UnusedClassifierPipeline.__name__,
                DBExportPipeline.__name__,
                SlackAlertPipeline.__name__,
            ]
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        raw_result: str = self.chain.run(title=adapter["title"]).upper()
        result: re.Match[bytes] | None = re.search(r"IPAD|MACBOOK|ETC", raw_result)

        try:
            category = result.group().upper()
            adapter["type"] = self.category_map[category]

        except IndexError or KeyError:
            raise DropAndAlert(item, "Not MacBook or iPad")

        adapter["pipelines"] = self.pipeline_map[adapter["type"]]
        return DBMacbookItem(**adapter) if adapter["type"] == "M" else DBIpadItem(**adapter)


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
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

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
            adapter["ssd"] = re.findall(r'SSD=(\S+)', predict)[0]
            if adapter["ssd"] == "1024GB" or adapter["ssd"] == "1024":
                adapter["ssd"] = "1TB"

        except Exception as e:
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

        return item


class IpadModelClassifierPipeline:
    name = "IpadModelClassifierPipeline"

    def __init__(self):
        self.ipad_chain: LLMChain = ipad_chain
        self.screen_size_map = {
            "MINI": 8.3,
            "IPAD": 12.9,
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
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}, {predict}")

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
                12.9: [8, 9, 10],
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
                raise DropAndAlert(item, f"[{self.name}]Unknown generation : {generation}")

        except Exception as e:
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

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
            adapter["ssd"] = re.findall(r'SSD=(\S+)', predict)[0]

            if adapter["ssd"] == "1024GB" or adapter["ssd"] == "1024":
                adapter["ssd"] = "1TB"

        except Exception as e:
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

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


class DBExportPipeline:
    name = "DBExportPipeline"

    def __init__(self):
        self.db = PostgresClient()
        self.cursor = self.db.getCursor()
        self.model_id_map = {
            "M": dict({
                "MINI": dict({
                    -1: 1
                }),
                "AIR": dict({
                    13: 2,
                }),
                "PRO": dict({
                    13: 3,
                    14: 4,
                    16: 5,
                })
            }),
            "P": dict({
                "IPADMINI": dict({
                    8.3: 6
                }),
                "IPADAIR": dict({
                    10.9: 7,
                }),
                "IPAD": dict({
                    12.9: 8,
                }),
                "IPADPRO": dict({
                    11: 9,
                    12.9: 10,
                })
            })
        }

    def classify_item_id(self, item: ItemAdapter) -> int:
        try:
            model_id = self.model_id_map[item["type"]][item["model"]][item["screen_size"]]

            if item["type"] == "M":
                if item["chip"] == "M1PRO":
                    item["chip"] = "M1Pro"
                elif item["chip"] == "M1MAX":
                    item["chip"] = "M1Max"
                elif item["chip"] == "M2PRO":
                    item["chip"] = "M2Pro"
                elif item["chip"] == "M2MAX":
                    item["chip"] = "M2Max"

                self.cursor.execute(
                    f"SELECT id "
                    f"FROM macguider.item_macbook "
                    f"WHERE model = {model_id} "
                    f"AND chip = '{item['chip']}' "
                    f"AND cpu = {item['cpu_core']} AND gpu = {item['gpu_core']} "
                    f"AND ssd = \'{item['ssd']}\' AND ram = {item['ram']} ")

                item_id = self.cursor.fetchone()[0]

                if item_id is None:
                    logging.error(
                        f"[{self.name}] item_id is None, model : {model_id}, chip : {item['chip']}, cpu : {item['cpu_core']}, gpu : {item['gpu_core']}, ssd : {item['ssd']}, ram : {item['ram']}")
            else:
                self.cursor.execute(
                    f"SELECT id "
                    f"FROM macguider.item_ipad "
                    f"WHERE model = {model_id} "
                    f"AND gen = {item['generation']} "
                    f"AND storage = \'{item['ssd']}\' "
                    f"AND cellular = {item['cellular']} "
                )

                item_id = self.cursor.fetchone()[0]

                if item_id is None:
                    logging.error(
                        f"[{self.name}] item_id is None, model : {model_id}, gen : {item['generation']}, storage : {item['storage']}, cellular : {item['cellular']}")
            return item_id
        except Exception as e:
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if type(self).__name__ not in adapter["pipelines"]:
            return item
        try:
            item_id = self.classify_item_id(adapter)
            item_type = adapter["type"]

            self.cursor.execute(
                f"UPDATE macguider.raw_used_item "
                f"SET item_id = {item_id}, type = '{item_type}', unused = {adapter['unused']} "
                f"WHERE id = {adapter['id']} "
            )

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

        return item


class HotDealClassifierPipeline:
    name = "HotDealClassifierPipeline"

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if adapter["price"] > adapter["average"]:
            raise DropItem("price is too high")
            # raise DropAndAlert(item, f"price is too high - price({adapter['price']}) > 95%({adapter['average'] * 0.95}), average - {adapter['average']} - {adapter['url']}")

        return item


class SoldOutClassifierPipeline:
    name = "SoldOutClassifierPipeline"

    def __init__(self):
        self.db = PostgresClient()
        self.cursor = self.db.getCursor()

    def set_sold_out(self, item: ItemAdapter):
        try:
            self.cursor.execute(
                f"UPDATE macguider.deal "
                f"SET sold = true "
                f"WHERE id = {item['id']} "
            )

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DropAndAlert(item, f"[{self.name}]Unknown error : {e}")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        logging.info(f"[{type(self).__name__}] start processing item: {adapter['id']}")

        if adapter["status"] != "SOLD_OUT":
            raise DropItem("item is on sale")

        self.set_sold_out(adapter)
        item["type"] = "SOLD_OUT"
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
        elif adapter["type"] == "P":
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
        elif adapter["type"] == "SOLD_OUT":
            self.slack_bot.post_soldout_message(
                url=adapter["id"],
            )
        else:
            self.slack_bot.post_hotdeal_message(
                url=adapter["url"],
                title=adapter["title"],
                source=adapter["source"],
                price=adapter["price"],
                average=adapter["average"],
            )
        return item
