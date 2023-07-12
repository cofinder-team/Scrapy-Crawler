import scrapy
import json
import datetime
import html
from scrapy_crawler.items import JgArticle


class JgMacbookAir13Spider(scrapy.Spider):
    name = "Jg_MacbookAir_13"

    def start_requests(self):
        yield scrapy.Request("https://apis.naver.com/cafe-web/cafe-mobile/CafeMobileWebArticleSearchListV3" +
                             "?cafeId=10050146&query=%EB%A7%A5%EB%B6%81%EC%97%90%EC%96%B4" +
                             "&searchBy=1&sortBy=date&page=1&perPage=50&adUnit=MW_CAFE_BOARD", self.parse)

    def parse(self, response):
        res = json.loads(response.text)["message"]["result"]["articleList"]

        non_sellers = list(filter(lambda x: x["memberLevel"] != 150, res))
        selling_articles = list(filter(lambda x: x["productSale"]["saleStatus"] == "SALE" or
                                                 x["productSale"]["saleStatus"] == "ESCROW", non_sellers))

        for article in selling_articles:
            yield scrapy.Request(
                f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/10050146/articles/{article['articleId']}",
                callback=self.parse_article,
                meta={
                    "article_url": f"https://cafe.naver.com/joonggonara/{article['articleId']}"
                })

    def parse_article(self, response):
        saleInfo = json.loads(response.text)["result"]["saleInfo"]
        article = json.loads(response.text)["result"]["article"]

        url = response.meta["article_url"]
        title = article["subject"]
        writer = article["writer"]["id"]

        # Convert timestamp to datetime
        date = datetime.datetime.fromtimestamp(article["writeDate"] / 1000).strftime("%Y-%m-%d %H:%M:%S")

        # Convert escaped html to normal html
        content = html.unescape(article["contentHtml"])

        price = saleInfo["price"]
        img_url = saleInfo["image"]["url"]

        yield JgArticle(url=url, title=title, writer=writer, date=date, content=content, price=price, img_url=img_url)




