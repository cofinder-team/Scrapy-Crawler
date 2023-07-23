SLACK_DROPPED_MESSAGE_TEMPLATE = lambda id, title, source, url, message: [
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"해당 게시물은 처리되지 않았습니다.\n사유 : {message}"},
    },
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*게시글 주소:*\n<{url}|{source}>"},
            {"type": "mrkdwn", "text": f"*게시글 제목:*\n{title}"},
        ],
    },
    {"type": "divider"},
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*지금 당장 수정하러 가기:*\n<{f'https://dev.macguider.io/deals/admin/{id}'}|{'수정 콘솔'}>",
        },
    },
]

SLACK_HOTDEAL_MESSAGE_TEMPLATE = lambda console_url: [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"핫딜 :fire:\nWEB CONSOLE: <{console_url}|{'웹 콘솔'}>",
        },
    },
]

SLACK_SOLDOUT_MESSAGE_TEMPLATE = lambda item_id: [
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"해당 글은 삭제 혹은 판매완료 되었습니다. - {item_id}"},
    },
]
