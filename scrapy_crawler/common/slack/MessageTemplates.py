def hotdeal_message_template(url: str, source: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"[{source}] <{url}|{'(구)웹 콘솔'}>",
            },
        },
    ]


def soldout_message_template(item_id):
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"해당 글은 삭제 혹은 판매완료 되었습니다. - {item_id}"},
        },
    ]
