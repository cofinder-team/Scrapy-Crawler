from enum import Enum


class DroppedCategoryEnum(Enum):
    Duplicate = "Duplicate"
    ForbiddenKeyword = "ForbiddenKeyword"
    LowPrice = "LowPrice"
    LongText = "LongText"
    UnsupportedCategory = "UnsupportedCategory"
    UnsupportedMacbook = "UnsupportedMacbook"
    UnsupportedIpad = "UnsupportedIpad"
    UnsupportedIphone = "UnsupportedIphone"
    Unknown = "Database Transaction Error"
