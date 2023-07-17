from scrapy.exceptions import DropItem
from scrapy_crawler.util.slack.SlackBots import LabelingSlackBot


class DropAndAlert(DropItem):
    def __init__(self, item, message="Custom Exception occurred"):
        self.item = item
        self.message = message
        LabelingSlackBot().post_fail_message(
            item['id'], item['title'], item['source'], item['url'], self.message
        )
        super().__init__(self.message)
