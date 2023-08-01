import scrapy


class ArticleItem(scrapy.Item):
    def __repr__(self):
        return f"ArticleItem({self['url']})"

    url = scrapy.Field()
    title = scrapy.Field()
    writer = scrapy.Field()
    content = scrapy.Field()
    price = scrapy.Field()
    img_url = scrapy.Field()
    date = scrapy.Field()
    status = scrapy.Field()
    source = scrapy.Field()
    raw_json = scrapy.Field()
    product_condition = scrapy.Field()


class ArticleStatus(scrapy.Item):
    def __repr__(self):
        return f"ArticleStatus({self['id']})"

    id = scrapy.Field()
    price = scrapy.Field()
    resp_status = scrapy.Field()
    prod_status = scrapy.Field()
