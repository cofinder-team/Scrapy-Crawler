from scrapy_crawler.Joonggonara.metadata.board_search import ArticleList
from scrapy_crawler.Joonggonara.utils.enums import (
    MemberLevel,
    ProductCondition,
    SaleStatus,
)


def is_official_seller(article: ArticleList) -> bool:
    return article.memberLevel == MemberLevel.OFFICIAL.value


def is_selling(article: ArticleList) -> bool:
    return (
        article.productSale.saleStatus == SaleStatus.SALE.value
        or article.productSale.saleStatus == SaleStatus.SAFE_SALE.value
    )


def is_used_item(product_condition: str) -> bool:
    return product_condition == ProductCondition.USED.value
