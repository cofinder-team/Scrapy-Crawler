import scrapy


class ArticleItem(scrapy.Item):
    def __repr__(self):
        return f"ArticleItem: {self['pid']}"

    pid = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    writer = scrapy.Field()
    price = scrapy.Field()
    img_url = scrapy.Field()
    prod_status = scrapy.Field()
    date = scrapy.Field()
    raw_json = scrapy.Field()
    source = scrapy.Field()
