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
        LabelingSlackBot().post_fail_message(
            item['id'], item['title'], item['source'], item['url'], self.message
        )

    def _set_classified(self, item):
        self.cursor.execute(
            "UPDATE macguider.raw_used_item SET classified = TRUE WHERE id = %s", (item['id'],)
        )
        self.db.commit()


