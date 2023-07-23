from scrapy.utils import project
from slack_sdk import WebClient

from scrapy_crawler.util.slack.MessageTemplates import (
    dropped_message_template,
    hotdeal_message_template,
    soldout_message_template,
)


class LabelingSlackBot:
    def __init__(self):
        self.settings = project.get_project_settings()
        self.slack_token = self.settings.get("SLACK_BOT_LABELING_TOKEN")
        self.slack_channel = self.settings.get("SLACK_CHANNEL_LABELING")
        self.slack_client = WebClient(token=self.slack_token)

    def post_fail_message(self, id, title, source, url, message):
        result = self.slack_client.chat_postMessage(
            channel="fail-alert",
            blocks=dropped_message_template(id, title, source, url, message),
        )

        return result

    def post_hotdeal_message(self, console_url, source):
        result = self.slack_client.chat_postMessage(
            channel="hotdeal-alert",
            blocks=hotdeal_message_template(console_url, source),
        )

        return result

    def post_soldout_message(self, url):
        result = self.slack_client.chat_postMessage(
            channel="soldout-alert", blocks=soldout_message_template(url)
        )

        return result
