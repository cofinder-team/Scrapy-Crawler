from enum import Enum

import requests
from scrapy import Selector
from scrapy.http import Response

from scrapy_crawler.common.utils.constants import FAKE_HEADER, Daangn


class DgArticleStatusEnum(Enum):
    SELLING = 1
    RESERVED = 2  # Can not check in WEB
    SOLD = 3
    HIDDEN = 4
    DELETED = 5

    @classmethod
    def from_response(cls, response: Response) -> "DgArticleStatusEnum":
        def is_hidden(s: Selector) -> bool:
            return s.css("#content #no-article").get() is not None

        def get_writer_id(s: Selector) -> str | None:
            writer_full_url = s.css("#content > #article-profile > a::attr(href)")
            if not writer_full_url:
                return None
            return writer_full_url.get().split("/")[-1]

        def get_selling_articles(id: str) -> list[str]:
            resp = requests.get(Daangn.PROFILE_URL % id, headers=FAKE_HEADER, timeout=5)

            resp.raise_for_status()
            profile_sel: Selector = Selector(text=resp.text)
            return list(
                map(
                    lambda x: x.split("/")[-1],
                    profile_sel.css(
                        "#user-records > section > article > a::attr(href)"
                    ).getall(),
                )
            )

        if response.status == 404:
            return cls.DELETED
        elif response.status != 200:
            raise Exception(
                f"Unexpected status code: {response.status}, {response.url}"
            )

        sel: Selector = Selector(text=response.text)
        if is_hidden(sel):
            return cls.HIDDEN
        elif (writer_id := get_writer_id(sel)) is None:
            return cls.DELETED

        articles = get_selling_articles(writer_id)
        if response.url.split("/")[-1] not in articles:
            return cls.SOLD

        return cls.SELLING
