import logging
from typing import Any

from botocore.client import BaseClient
import boto3
from langchain.callbacks.base import BaseCallbackHandler
import time

from langchain.schema import LLMResult


class CloudWatchCallbackHandler(BaseCallbackHandler):
    def __init__(self, log_group_name, log_stream_name, function_name):
        from scrapy.utils import project

        settings = project.get_project_settings()
        self.log_group_name = log_group_name
        self.log_stream_name = str(log_stream_name)

        self.cloudwatch_client: BaseClient = boto3.client(
            "logs",
            aws_access_key_id=settings.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=settings.get("AWS_SECRET_ACCESS_KEY"),
            region_name="ap-northeast-2",
        )

        try:
            self.cloudwatch_client.create_log_stream(
                logGroupName=self.log_group_name, logStreamName=self.log_stream_name
            )
        except self.cloudwatch_client.exceptions.ResourceAlreadyExistsException:
            pass

        self.function_name = function_name

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
