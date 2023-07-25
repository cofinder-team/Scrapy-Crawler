import scrapy


class DBItem(scrapy.Item):
    # DB data
    id = scrapy.Field()
    writer = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    price = scrapy.Field()
    source = scrapy.Field()
    date = scrapy.Field()
    url = scrapy.Field()
    img_url = scrapy.Field()
    type = scrapy.Field()
    item_id = scrapy.Field()

    # for category
    category = scrapy.Field()
    pipelines = scrapy.Field()


class DBMacbookItem(DBItem):
    chip = scrapy.Field()
    cpu_core = scrapy.Field()
    gpu_core = scrapy.Field()
    ram = scrapy.Field()
    model = scrapy.Field()
    screen_size = scrapy.Field()
    ssd = scrapy.Field()
    unused = scrapy.Field()
    apple_care_plus = scrapy.Field()


class DBIpadItem(DBItem):
    model = scrapy.Field()
    screen_size = scrapy.Field()
    ssd = scrapy.Field()
    unused = scrapy.Field()
    apple_care_plus = scrapy.Field()
    generation = scrapy.Field()
    cellular = scrapy.Field()


class JgArticle(scrapy.Item):
    id = scrapy.Field()
    price = scrapy.Field()
    status = scrapy.Field()
    type = scrapy.Field()


class DealItem(scrapy.Item):
    id = scrapy.Field()
    type = scrapy.Field()
    item_id = scrapy.Field()
    price = scrapy.Field()
    sold = scrapy.Field()
    unused = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    date = scrapy.Field()
    last_crawled = scrapy.Field()
    writer = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    apple_care = scrapy.Field()
