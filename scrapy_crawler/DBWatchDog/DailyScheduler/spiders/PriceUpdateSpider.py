from datetime import datetime, timedelta
from typing import List

import scrapy
from sqlalchemy import null, true
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import Deal, get_engine
from scrapy_crawler.common.db.models import Trade
from scrapy_crawler.common.utils.helpers import init_cloudwatch_logger


class PriceUpdateSpider(scrapy.Spider):
    name = "PriceUpdateSpider"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_cloudwatch_logger(self.name)
        self.session = sessionmaker(bind=get_engine())()

    def start_requests(self):
        yield scrapy.Request(
            url="https://google.com",
            callback=self.parse,
        )

    def get_soldout_items(self) -> List[Deal]:
        item = (
            self.session.query(Deal)
            .filter(Deal.sold == true())
            .filter(Deal.deleted_at == null())
            .filter(Deal.condition == "S")
            .filter(Deal.last_crawled > datetime.now() - timedelta(days=1))
        )
        return item.all()

    def trade_exist(self, entity: Deal) -> bool:
        item = (
            self.session.query(Trade)
            .filter(Trade.type == entity.type)
            .filter(Trade.item_id == entity.item_id)
            .filter(Trade.unused == entity.unused)
            .filter(Trade.source == entity.source)
            .filter(Trade.writer == entity.writer)
        )
        return item.count() > 0

    def parse(self, response, **kwargs):
        self.logger.info("Start PriceUpdateSpider")
        soldout_items = self.get_soldout_items()
        self.logger.info(f"Found {len(soldout_items)} soldout items")

        try:
            for item in soldout_items:
                if self.trade_exist(item):
                    self.logger.info(f"Trade already exist: {item}")

                    # Update price, date
                    (
                        self.session.query(Trade)
                        .filter(Trade.type == item.type)
                        .filter(Trade.item_id == item.item_id)
                        .filter(Trade.unused == item.unused)
                        .filter(Trade.source == item.source)
                        .filter(Trade.writer == item.writer)
                        .update({Trade.price: item.price, Trade.date: item.date})
                    )
                    continue

                # Add to trade
                trade = Trade(
                    type=item.type,
                    item_id=item.item_id,
                    price=item.price,
                    date=item.date,
                    unused=item.unused,
                    care=item.apple_care,
                    url=item.url,
                    source=item.source,
                    title=item.title,
                    content=item.content,
                    writer=item.writer,
                )

                self.session.add(trade)
            self.session.commit()
            self.logger.info("Successfully updated price")
        except Exception as e:
            self.logger.error(f"Failed to update price: {e}")
            self.session.rollback()
