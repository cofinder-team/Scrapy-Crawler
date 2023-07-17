from scrapy.utils import project
from slack_sdk import WebClient
from scrapy_crawler.util.slack.MessageTemplates import *


class LabelingSlackBot(object):
    def __init__(self):
        self.settings = project.get_project_settings()
        self.slack_token = self.settings.get('SLACK_BOT_LABELING_TOKEN')
        self.slack_channel = self.settings.get('SLACK_CHANNEL_LABELING')
        self.slack_client = WebClient(token=self.slack_token)

    def post_macbook_message(self, url, source, title, model, screen_size, chip, cpu, ram, ssd, unused, apple_care_plus,
                             id):
        result = self.slack_client.chat_postMessage(
            channel="데이터-라벨링",
            blocks=SLACK_MACBOOK_CLASSIFY_MESSAGE_TEMPLATE(
                url, source, title, model, screen_size, chip, cpu, ram, ssd, unused, apple_care_plus, id
            )
        )

        return result

    def post_ipad_message(self, url, source, title, model, screen_size, gen, cellular, ssd, unused, apple_care_plus,
                          id):
        result = self.slack_client.chat_postMessage(
            channel="데이터-라벨링",
            blocks=SLACK_IPAD_CLASSIFY_MESSAGE_TEMPLATE(
                url, source, title, model, screen_size, gen, cellular, ssd, unused, apple_care_plus, id
            )
        )

        return result
