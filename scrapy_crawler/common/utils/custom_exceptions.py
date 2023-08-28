from scrapy.exceptions import DropItem


class DropDuplicateItem(DropItem):
    def __init__(self, *args):
        super().__init__(*args)


class DropForbiddenKeywordItem(DropItem):
    def __init__(self, *args):
        super().__init__(*args)


class DropTooLowPriceItem(DropItem):
    def __init__(self, *args):
        super().__init__(*args)


class DropTooLongTextItem(DropItem):
    def __init__(self, *args):
        super().__init__(*args)
