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

    # Macbook or iPad?
    category = scrapy.Field()
    pipelines = scrapy.Field()

    # for macbook
    chip = scrapy.Field()
    cpu_core = scrapy.Field()
    gpu_core = scrapy.Field()
    ram = scrapy.Field()

    # for ipad
    generation = scrapy.Field()
    cellular = scrapy.Field()

    # for both
    model = scrapy.Field()
    screen_size = scrapy.Field()
    ssd = scrapy.Field()
    unused = scrapy.Field()
    apple_care_plus = scrapy.Field()