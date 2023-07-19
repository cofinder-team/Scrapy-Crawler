from scrapy.exceptions import DropItem

from scrapy_crawler.util.db.Postgres import PostgresClient
from scrapy_crawler.util.slack.SlackBots import LabelingSlackBot


class DropAndAlert(DropItem):
    def __init__(self, item, message="Custom Exception occurred"):
        self.item = item
        self.message = message
        self.db = PostgresClient()
        self.cursor = self.db.getCursor()

        super().__init__(self.message)
        self._notify_message(item)
        self._set_classified(item)

    def _notify_message(self, item):
        id = item['id'] if 'id' in item else 'NONE'
        title = item['title'] if 'title' in item else 'NONE'
        source = item['source'] if 'source' in item else 'NONE'
        url = item['url'] if 'url' in item else 'NONE'

        LabelingSlackBot().post_fail_message(
            id, title, source, url, self.message
        )

    def _set_classified(self, item):
        self.cursor.execute(
            "UPDATE macguider.raw_used_item SET classified = TRUE WHERE id = %s", (item['id'],)
        )
        self.db.commit()


