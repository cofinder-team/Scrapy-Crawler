def dropped_message_template(id: str, title: str, source: str, url: str, message: str):
    return [
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


def hotdeal_message_template(url: str, source: str):
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"핫딜 :fire:\n출처 : {source}\nCONSOLE: <{url}|{'웹 콘솔'}>",
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
