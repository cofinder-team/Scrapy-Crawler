CONSOLE_URL = "https://macguider.io/deals/admin/%s"
NEW_CONSOLE_URL = "https://macguider.io/deals/report/%s"

FAKE_HEADER = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Mobile Safari/537.36"
}


class BunJang:
    TOTAL_SEARCH_API_URL = (
        "https://api.bunjang.co.kr/api/1/find_v2.json?n=30&page=0&req_ref=search&q=%s&version=4&order"
        "=date"
    )
    ARTICLE_API_URL = (
        "https://api.bunjang.co.kr/api/pms/v2/products-detail/%s?viewerUid=-1"
    )
    ARTICLE_URL = "https://m.bunjang.co.kr/products/%s"


class Joonggonara:
    NOTEBOOK_BOARD_FETCH_URL = (
        "https://apis.naver.com/cafe-web/cafe-mobile/CafeMobileWebArticleSearchListV3?cafeId"
        "=10050146&menuId=334&query=%s&searchBy=1&sortBy=date&page=1&perPage=50&adUnit=MW_CAFE_BOARD"
    )

    TOTAL_SEARCH_FETCH_URL = (
        "https://apis.naver.com/cafe-web/cafe-mobile/CafeMobileWebArticleSearchListV3?cafeId"
        "=10050146&query=%s&searchBy=0&sortBy=date&page=1&perPage=50&adUnit=MW_CAFE_BOARD"
    )
    ARTICLE_API_URL = "https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/10050146/articles/%s"
    ARTICLE_URL = "https://cafe.naver.com/joonggonara/%s"
