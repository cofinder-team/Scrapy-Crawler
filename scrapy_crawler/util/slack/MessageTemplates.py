SLACK_MACBOOK_CLASSIFY_MESSAGE_TEMPLATE = lambda url, source, title, model, screen_size, chip, cpu, ram, ssd, unused, apple_care_plus, id: [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*게시글 주소:*\n<{url}|{source}>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*지금 당장 수정하러 가기:*\n<{f'www.dev.macguider.io/deals/admin/{id}'}|{'수정 콘솔'}>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*게시글 제목:*\n{title}"
        }
    },
    {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*종류:*\n맥북"
            },
            {
                "type": "mrkdwn",
                "text": f"*MODEL:*\n{model}"
            },
            {
                "type": "mrkdwn",
                "text": f"*SCREEN_SIZE:*\n{screen_size}"
            },
            {
                "type": "mrkdwn",
                "text": f"*CHIP:*\n{chip}"
            },
            {
                "type": "mrkdwn",
                "text": f"*CORE:*\n{cpu}"
            },
            {
                "type": "mrkdwn",
                "text": f"*RAM*\n{ram}"
            },
            {
                "type": "mrkdwn",
                "text": f"*SSD:*\n{ssd}"
            },
            {
                "type": "mrkdwn",
                "text": f"*미개봉/중고:*\n{'미개봉' if unused else '중고'}"
            },
            # {
            #     "type": "mrkdwn",
            #     "text": f"*애플케어플러스*\n{'있음' if apple_care_plus else '없음'}"
            # }
        ]
    },
    {
        "type": "divider"
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "TRUE"
                },
                "style": "primary",
                "value": "true"
            },
        ]
    },
]

SLACK_IPAD_CLASSIFY_MESSAGE_TEMPLATE = lambda url, source, title, model, screen_size, gen, cellular, ssd, unused, apple_care_plus, id: [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*게시글 주소:*\n<{url}|{source}>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*지금 당장 수정하러 가기:*\n<{f'www.dev.macguider.io/deals/admin/{id}'}|{'수정 콘솔'}>"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*게시글 제목:*\n{title}"
        }
    },
    {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*종류:*\n아이패드"
            },
            {
                "type": "mrkdwn",
                "text": f"*MODEL:*\n{model}"
            },
            {
                "type": "mrkdwn",
                "text": f"*SCREEN_SIZE:*\n{screen_size}"
            },
            {
                "type": "mrkdwn",
                "text": f"*GEN:*\n{gen}"
            },
            {
                "type": "mrkdwn",
                "text": f"*CELLULAR:*\n{cellular}"
            },
            {
                "type": "mrkdwn",
                "text": f"*SSD:*\n{ssd}"
            },
            {
                "type": "mrkdwn",
                "text": f"*미개봉/중고:*\n{'미개봉' if unused else '중고'}"
            },
            # {
            #     "type": "mrkdwn",
            #     "text": f"*애플케어플러스*\n{'있음' if apple_care_plus else '없음'}"
            # }
        ]
    },
    {
        "type": "divider"
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "TRUE"
                },
                "style": "primary",
                "value": "true"
            },
        ]
    },

]

