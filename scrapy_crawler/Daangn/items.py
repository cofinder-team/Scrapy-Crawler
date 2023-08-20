import scrapy


class ArticleItem(scrapy.Item):
    def __repr__(self):
        return f"ArticleItem({self['url']})"

    id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    writer = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    img_url = scrapy.Field()
