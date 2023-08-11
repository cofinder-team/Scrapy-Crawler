def hotdeal_message_template(url: str, source: str, msg):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"[라벨링 요청][{source}] <{url}|{'웹 콘솔'}> : {msg}",
            },
        },
    ]


def labeling_message_template(url: str, msg: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"[메뉴얼 분류] <{url}|{'(구)웹 콘솔'}> : {msg}",
            },
        },
    ]
