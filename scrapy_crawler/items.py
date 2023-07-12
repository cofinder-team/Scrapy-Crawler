# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class JgArticle(scrapy.Item):
    url = scrapy.Field()
    img_url = scrapy.Field()
    price = scrapy.Field()
    date = scrapy.Field()
    writer = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
