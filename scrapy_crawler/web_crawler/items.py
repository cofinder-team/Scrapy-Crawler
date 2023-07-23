import scrapy


class JgArticle(scrapy.Item):
    url = scrapy.Field()
    img_url = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()
    writer = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()


class BungaeArticle(scrapy.Item):
    pid = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    product_image = scrapy.Field()
    bun_pay_filter_enabled = scrapy.Field()
    tag = scrapy.Field()
    update_time = scrapy.Field()
    used = scrapy.Field()
    etc = scrapy


class BungaeArticleDetail(scrapy.Item):
    pid = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    writer = scrapy.Field()
    price = scrapy.Field()
    saleStatus = scrapy.Field()
    status = scrapy.Field()
    imageUrl = scrapy.Field()
    updatedAt = scrapy.Field()
    source = scrapy.Field()
