from scrapy.utils import project
from slack_sdk import WebClient

from scrapy_crawler.common.slack.MessageTemplates import (
    hotdeal_message_template,
    labeling_message_template,
)


class LabelingSlackBot:
    def __init__(self):
        self.settings = project.get_project_settings()
        self.slack_token = self.settings.get("SLACK_BOT_LABELING_TOKEN")
        self.slack_channel = self.settings.get("SLACK_CHANNEL_LABELING")
        self.slack_client = WebClient(token=self.slack_token)

    def post_hotdeal_message(self, console_url, source, msg: str = ""):
        result = self.slack_client.chat_postMessage(
            channel="hotdeal-alert",
            blocks=hotdeal_message_template(console_url, source, msg),
        )

        return result

    def post_labeling_message(self, console_url, msg):
        result = self.slack_client.chat_postMessage(
            channel="hotdeal-alert",
            blocks=labeling_message_template(console_url, msg),
        )

        return result
