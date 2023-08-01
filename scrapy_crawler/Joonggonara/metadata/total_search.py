from dataclasses import dataclass
from typing import Any, List


@dataclass
class ArticleList:
    cafeId: int
    menuId: int
    articleId: int
    subject: str
    summary: str
    thumbnailImageUrl: str
    memberNickName: str
    memberKey: str
    likeItCount: int
    readCount: int
    commentCount: int
    imageAttachCount: int
    addDate: str
    currentSecTime: str
    productSale: "ProductSale"
    boardType: str
    menuType: str
    highlightKeywords: List[object]
    sc: str
    cafeMenuReadlevel: int
    memberLevel: int
    memberLevelIconId: int
    representImageType: str

    @staticmethod
    def from_dict(obj: Any) -> "ArticleList":
        _cafeId = int(obj.get("cafeId"))
        _menuId = int(obj.get("menuId"))
        _articleId = int(obj.get("articleId"))
        _subject = str(obj.get("subject"))
        _summary = str(obj.get("summary"))
        _thumbnailImageUrl = str(obj.get("thumbnailImageUrl"))
        _memberNickName = str(obj.get("memberNickName"))
        _memberKey = str(obj.get("memberKey"))
        _likeItCount = int(obj.get("likeItCount"))
        _readCount = int(obj.get("readCount"))
        _commentCount = int(obj.get("commentCount"))
        _imageAttachCount = int(obj.get("imageAttachCount"))
        _addDate = str(obj.get("addDate"))
        _currentSecTime = str(obj.get("currentSecTime"))
        _productSale = ProductSale.from_dict(obj.get("productSale"))
        _boardType = str(obj.get("boardType"))
        _menuType = str(obj.get("menuType"))
        _highlightKeywords = [y for y in obj.get("highlightKeywords")]
        _sc = str(obj.get("sc"))
        _cafeMenuReadlevel = int(obj.get("cafeMenuReadlevel"))
        _memberLevel = int(obj.get("memberLevel"))
        _memberLevelIconId = int(obj.get("memberLevelIconId"))
        _representImageType = str(obj.get("representImageType"))
        return ArticleList(
            _cafeId,
            _menuId,
            _articleId,
            _subject,
            _summary,
            _thumbnailImageUrl,
            _memberNickName,
            _memberKey,
            _likeItCount,
            _readCount,
            _commentCount,
            _imageAttachCount,
            _addDate,
            _currentSecTime,
            _productSale,
            _boardType,
            _menuType,
            _highlightKeywords,
            _sc,
            _cafeMenuReadlevel,
            _memberLevel,
            _memberLevelIconId,
            _representImageType,
        )


@dataclass
class Error:
    code: str
    msg: str

    @staticmethod
    def from_dict(obj: Any) -> "Error":
        _code = str(obj.get("code"))
        _msg = str(obj.get("msg"))
        return Error(_code, _msg)


@dataclass
class Message:
    status: str
    error: Error
    result: "Result"

    @staticmethod
    def from_dict(obj: Any) -> "Message":
        _status = str(obj.get("status"))
        _error = Error.from_dict(obj.get("error"))
        _result = Result.from_dict(obj.get("result"))
        return Message(_status, _error, _result)


@dataclass
class ProductSale:
    saleStatus: str
    cost: str
    deliveryTypeList: List[str]
    regionList: List[object]

    @staticmethod
    def from_dict(obj: Any) -> "ProductSale":
        _saleStatus = str(obj.get("saleStatus"))
        _cost = str(obj.get("cost"))
        _deliveryTypeList = (
            [y for y in obj.get("deliveryTypeList")]
            if obj.get("deliveryTypeList")
            else []
        )
        _regionList = (
            [y for y in obj.get("regionList")] if obj.get("regionList") else []
        )
        return ProductSale(_saleStatus, _cost, _deliveryTypeList, _regionList)


@dataclass
class Result:
    cafeId: int
    totalArticleCount: int
    articleCount: int
    perPage: int
    page: int
    query: str
    searchBy: int
    sortBy: str
    articleList: List[ArticleList]

    @staticmethod
    def from_dict(obj: Any) -> "Result":
        _cafeId = int(obj.get("cafeId"))
        _totalArticleCount = int(obj.get("totalArticleCount"))
        _articleCount = int(obj.get("articleCount"))
        _perPage = int(obj.get("perPage"))
        _page = int(obj.get("page"))
        _query = str(obj.get("query"))
        _searchBy = int(obj.get("searchBy"))
        _sortBy = str(obj.get("sortBy"))
        _articleList = [ArticleList.from_dict(y) for y in obj.get("articleList")]
        return Result(
            _cafeId,
            _totalArticleCount,
            _articleCount,
            _perPage,
            _page,
            _query,
            _searchBy,
            _sortBy,
            _articleList,
        )


@dataclass
class TotalSearchRoot:
    message: Message

    @staticmethod
    def from_dict(obj: Any) -> "TotalSearchRoot":
        _message = Message.from_dict(obj.get("message"))
        return TotalSearchRoot(_message)
