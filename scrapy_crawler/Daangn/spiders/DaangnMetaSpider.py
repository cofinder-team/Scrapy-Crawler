from typing import Type

import scrapy
from scrapy import Selector
from scrapy.http import Response
from sqlalchemy import null, true
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.common.db import RawUsedItem, get_engine
from scrapy_crawler.common.enums import DgArticleStatusEnum, SourceEnum
from scrapy_crawler.Daangn.items import ArticleItem


class DaangnMetaSpider(scrapy.Spider):
    name = "DaangnMetaSpider"
    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapy_crawler.Daangn.pipelines.InitCloudwatchLogger": 1,
            "scrapy_crawler.Daangn.pipelines.PersistPipeline": 2,
        }
    }

    def __init__(self):
        super().__init__()
        self.session = sessionmaker(bind=get_engine())()

    def get_uncrawled_items(self) -> list[Type[RawUsedItem]]:
        items = (
            self.session.query(RawUsedItem)
            .filter(RawUsedItem.source == SourceEnum.DAANGN.value)
            .filter(RawUsedItem.type == null())
            .filter(RawUsedItem.item_id == null())
            .filter(RawUsedItem.title == null())
            .all()
        )

        return items

    def start_requests(self):
        items = self.get_uncrawled_items()

        for item in items:
            yield scrapy.Request(
                url=item.url, callback=self.parse, meta={"url": item.url, "id": item.id}
            )

    def get_price(self, sel: Selector) -> int:
        price = sel.css(
            "#content > #article-description > #article-price::attr(content)"
        ).get()

        return int(price.split(".")[0]) if price.split(".")[0] != "" else 0

    def parse(self, response: Response):
        url = response.meta["url"]
        id = response.meta["id"]
        article_status = DgArticleStatusEnum.from_response(response)

        if article_status == DgArticleStatusEnum.SELLING:
            sel: Selector = Selector(response)
            title = sel.css("#content > h1::text").get()
            content = "".join(
                sel.css(
                    "#content > #article-description > #article-detail > p::text"
                ).getall()
            )
            writer = (
                sel.css("#content > #article-profile > a::attr(href)")
                .get()
                .split("/")[-1]
            )

            if (price := self.get_price(sel)) == 0:  # 나눔
                return None

            img_url = (
                sel.css("meta[property='og:image']::attr(content)")
                .get()
                .replace("s=1440x1440", "s=300x300")
                .replace("&f=webp", "")
            )

            yield ArticleItem(
                id=id,
                url=url,
                title=title,
                writer=writer,
                content=content,
                price=price,
                img_url=img_url,
            )
        elif article_status == DgArticleStatusEnum.DELETED:
            self.session.query(RawUsedItem).filter(RawUsedItem.id == id).update(
                {RawUsedItem.classified: true()}
            )
            self.session.commit()
            return None
