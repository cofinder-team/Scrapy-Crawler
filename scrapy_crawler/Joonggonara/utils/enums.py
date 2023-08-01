from enum import Enum


class SaleStatus(Enum):
    SALE = "SALE"
    SAFE_SALE = "ESCROW"
    RESERVED = "RESERVED"
    SOLD_OUT = "SOLD_OUT"


class MemberLevel(Enum):
    NORMAL = 0
    OFFICIAL = 150


class ProductCondition(Enum):
    # 미개봉
    NEW = "NEW"

    # 거의 새것
    ALMOST_NEW = "ALMOST_NEW"

    # 사용감 있음
    USED = "USED"
