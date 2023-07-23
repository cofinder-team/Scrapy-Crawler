from scrapy.utils import project
from slack_sdk import WebClient
from scrapy_crawler.util.slack.MessageTemplates import *


class LabelingSlackBot(object):
    def __init__(self):
        self.settings = project.get_project_settings()
        self.slack_token = self.settings.get("SLACK_BOT_LABELING_TOKEN")
        self.slack_channel = self.settings.get("SLACK_CHANNEL_LABELING")
        self.slack_client = WebClient(token=self.slack_token)

    def post_fail_message(self, id, title, source, url, message):
        result = self.slack_client.chat_postMessage(
            channel="fail-alert",
            blocks=SLACK_DROPPED_MESSAGE_TEMPLATE(id, title, source, url, message),
        )

        return result

    def post_hotdeal_message(self, console_url):
        result = self.slack_client.chat_postMessage(
            channel="hotdeal-alert", blocks=SLACK_HOTDEAL_MESSAGE_TEMPLATE(console_url)
        )

        return result

    def post_soldout_message(self, url):
        result = self.slack_client.chat_postMessage(
            channel="soldout-alert", blocks=SLACK_SOLDOUT_MESSAGE_TEMPLATE(url)
        )

        return result
