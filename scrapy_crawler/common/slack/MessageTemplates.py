def hotdeal_message_template(url: str, source: str, msg):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"[{source}] <{url}|{'(구)웹 콘솔'}> : {msg}",
            },
        },
    ]
