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
        spider.logger.info(
            f"[{type(self).__name__}][{item['log_id']}] start process_item"
        )
        adapter = ItemAdapter(item)

        try:
            self.session.query(Deal).filter(Deal.id == adapter["id"]).update(
                {Deal.last_crawled: get_local_timestring()}
            )
            self.session.commit()
            spider.logger.info(
                f"[{type(self).__name__}][{adapter['log_id']}] Update last_crawled"
            )
        except Exception as e:
            spider.logger.error(
                f"[{type(self).__name__}][{adapter['log_id']}] {e.__class__.__name__}: {e}"
            )
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
        spider.logger.info(
            f"[{type(self).__name__}][{item['log_id']}] start process_item"
        )
        adapter = ItemAdapter(item)

        id, log_stream_id, resp_status, prod_status = (
            adapter["id"],
            adapter["log_id"],
            adapter["resp_status"],
            adapter["prod_status"],
        )

        if prod_status == "SOLD_OUT":
            try:
                self.session.query(Deal).filter(Deal.id == id).update(
                    {Deal.sold: true()}
                )
                self.session.commit()
                spider.logger.info(
                    f"[{type(self).__name__}][{log_stream_id}] Update sold status"
                )
            except Exception as e:
                spider.logger.error(
                    f"[{type(self).__name__}][{log_stream_id}] {e.__class__.__name__}: {e}"
                )
                self.session.rollback()

        elif resp_status == 200:
            spider.logger.info(
                f"[{type(self).__name__}][{log_stream_id}] Current prod_status to {prod_status}"
            )

        return item
