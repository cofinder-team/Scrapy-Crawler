import logging

from itemadapter import ItemAdapter
from sqlalchemy import true
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import Deal, get_engine
from scrapy_crawler.common.utils import get_local_timestring


class UpdateLastCrawledTime:
    name = "UpdateLastCrawledTime"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        try:
            self.session.query(Deal).filter(Deal.id == adapter["id"]).update(
                {Deal.last_crawled: get_local_timestring()}
            )
            self.session.commit()
            logging.warning(f"Update last_crawled time of {adapter['id']}")
        except Exception as e:
            logging.error(e)
            self.session.rollback()

        return item


class UpdateSoldStatus:
    name = "UpdateSoldStatus"

    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = sessionmaker(bind=get_engine())()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        id, resp_status, prod_status = (
            adapter["id"],
            adapter["resp_status"],
            adapter["prod_status"],
        )

        if resp_status == 404 or prod_status == "SOLD_OUT":
            try:
                self.session.query(Deal).filter(Deal.id == id).update(
                    {Deal.sold: true()}
                )
                self.session.commit()
                logging.warning(f"Update status of {id} to SOLD_OUT")
            except Exception as e:
                logging.error(e)
                self.session.rollback()

        elif resp_status == 200:
            logging.warning(f"Status of {id} to {prod_status}")

        return item
