from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker

from scrapy_crawler.util.db.models import RawUsedItem
from scrapy_crawler.util.db.settings import get_engine
from scrapy_crawler.util.slack.SlackBots import LabelingSlackBot


class DropAndAlert(DropItem):
    def __init__(self, item, message="Custom Exception occurred"):
        super().__init__(message)
        self.item = item
        self.message = message
        self.session = sessionmaker(bind=get_engine())()
        self._notify_message(item)
        self._set_classified(item)

    def _notify_message(self, item):
        id = item["id"] if "id" in item else "NONE"
        title = item["title"] if "title" in item else "NONE"
        source = item["source"] if "source" in item else "NONE"
        url = item["url"] if "url" in item else "NONE"

        LabelingSlackBot().post_fail_message(id, title, source, url, self.message)

    def _set_classified(self, item):
        self.session.query(RawUsedItem).filter(RawUsedItem.id == item["id"]).update(
            {RawUsedItem.classified: True}
        )
        self.session.commit()
