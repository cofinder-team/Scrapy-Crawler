import scrapy


class JgArticle(scrapy.Item):
    url = scrapy.Field()
    img_url = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()
    writer = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
