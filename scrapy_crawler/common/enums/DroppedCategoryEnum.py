from enum import Enum


class DroppedCategoryEnum(Enum):
    Duplicate = "Duplicate"
    ForbiddenKeyword = "ForbiddenKeyword"
    LowPrice = "LowPrice"
    LongText = "LongText"
    Unknown = "Database Transaction Error"
