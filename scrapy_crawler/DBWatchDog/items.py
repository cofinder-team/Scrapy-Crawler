import scrapy


class UnClassifiedItem(scrapy.Item):
    def __repr__(self):
        return f"UnClassifiedItem(id={self['id']}, title={self['title']})"

    id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    item_id = scrapy.Field()
    model = scrapy.Field()


class MacbookItem(UnClassifiedItem):
    def __repr__(self):
        return f"MacBookItem(id={self['id']}, title={self['title']})"

    screen_size = scrapy.Field()
    chip = scrapy.Field()
    cpu_core = scrapy.Field()
    gpu_core = scrapy.Field()
    ram = scrapy.Field()
    ssd = scrapy.Field()
    unused = scrapy.Field()
    apple_care_plus = scrapy.Field()


class IpadItem(UnClassifiedItem):
    def __repr__(self):
        return f"IpadItem(id={self['id']}, title={self['title']})"

    screen_size = scrapy.Field()
    ssd = scrapy.Field()
    unused = scrapy.Field()
    apple_care_plus = scrapy.Field()
    generation = scrapy.Field()
    cellular = scrapy.Field()


class IphoneItem(UnClassifiedItem):
    def __repr__(self):
        return f"IphoneItem(id={self['id']}, title={self['title']})"

    ssd = scrapy.Field()
    unused = scrapy.Field()
    generation = scrapy.Field()
    apple_care_plus = scrapy.Field()
