import time
from typing import Any

import boto3
from botocore.client import BaseClient
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from scrapy.utils import project


class CloudWatchCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.log_group_name = None
        self.log_stream_name = None
        self.function_name = None

        settings = project.get_project_settings()
        self.cloudwatch_client: BaseClient = boto3.client(
            "logs",
            aws_access_key_id=settings.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=settings.get("AWS_SECRET_ACCESS_KEY"),
            region_name="ap-northeast-2",
        )

    def set_meta_data(self, function_name: str, log_stream_name: str):
        self.log_group_name = "scrapy-chatgpt"
        self.function_name = function_name
        self.log_stream_name = log_stream_name

        try:
            self.cloudwatch_client.create_log_stream(
                logGroupName=self.log_group_name, logStreamName=self.log_stream_name
            )
        except self.cloudwatch_client.exceptions.ResourceAlreadyExistsException:
            pass

        return self

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        self.cloudwatch_client.put_log_events(
            logGroupName=self.log_group_name,
            logStreamName=self.log_stream_name,
            logEvents=[
                {
                    "timestamp": int(time.time() * 1000),
                    "message": f"[{self.function_name}] {response}",
                }
            ],
        )
