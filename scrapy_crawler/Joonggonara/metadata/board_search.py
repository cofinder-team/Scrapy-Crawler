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
    representImageType: str
    addDate: str
    currentSecTime: str
    cafeBookYn: bool
    productSale: "ProductSale"
    attachMusic: bool
    attachFileInArticle: bool
    attachPollInArticle: bool
    attachMap: bool
    attachCalendar: bool
    attachGpx: bool
    attachLink: bool
    newArticle: bool
    boardType: str
    menuType: str
    bookArticle: bool
    staffArticle: bool
    simpleArticle: bool
    replyArticle: bool
    marketArticle: bool
    highlightKeywords: List[object]
    sc: str
    delParent: bool
    cafeMenuReadlevel: int
    memberLevel: int
    memberLevelIconId: int
    popular: bool

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
        _representImageType = str(obj.get("representImageType"))
        _addDate = str(obj.get("addDate"))
        _currentSecTime = str(obj.get("currentSecTime"))
        _cafeBookYn = obj.get("cafeBookYn")
        _productSale = ProductSale.from_dict(obj.get("productSale"))
        _attachMusic = obj.get("attachMusic")
        _attachFileInArticle = obj.get("attachFileInArticle")
        _attachPollInArticle = obj.get("attachPollInArticle")
        _attachMap = obj.get("attachMap")
        _attachCalendar = obj.get("attachCalendar")
        _attachGpx = obj.get("attachGpx")
        _attachLink = obj.get("attachLink")
        _newArticle = obj.get("newArticle")
        _boardType = str(obj.get("boardType"))
        _menuType = str(obj.get("menuType"))
        _bookArticle = obj.get("bookArticle")
        _staffArticle = obj.get("staffArticle")
        _simpleArticle = obj.get("simpleArticle")
        _replyArticle = obj.get("replyArticle")
        _marketArticle = obj.get("marketArticle")
        _highlightKeywords = [y for y in obj.get("highlightKeywords")]
        _sc = str(obj.get("sc"))
        _delParent = obj.get("delParent")
        _cafeMenuReadlevel = int(obj.get("cafeMenuReadlevel"))
        _memberLevel = int(obj.get("memberLevel"))
        _memberLevelIconId = int(obj.get("memberLevelIconId"))
        _popular = obj.get("popular")
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
            _representImageType,
            _addDate,
            _currentSecTime,
            _cafeBookYn,
            _productSale,
            _attachMusic,
            _attachFileInArticle,
            _attachPollInArticle,
            _attachMap,
            _attachCalendar,
            _attachGpx,
            _attachLink,
            _newArticle,
            _boardType,
            _menuType,
            _bookArticle,
            _staffArticle,
            _simpleArticle,
            _replyArticle,
            _marketArticle,
            _highlightKeywords,
            _sc,
            _delParent,
            _cafeMenuReadlevel,
            _memberLevel,
            _memberLevelIconId,
            _popular,
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
    regionList: List["RegionList"]

    @staticmethod
    def from_dict(obj: Any) -> "ProductSale":
        _saleStatus = str(obj.get("saleStatus"))
        _cost = str(obj.get("cost"))
        _deliveryTypeList = [y for y in obj.get("deliveryTypeList")]
        _regionList = [RegionList.from_dict(y) for y in obj.get("regionList")]
        return ProductSale(_saleStatus, _cost, _deliveryTypeList, _regionList)


@dataclass
class RegionList:
    cafeId: int
    articleId: int
    regionCode1: str
    regionName1: str
    regionCode2: str
    regionName2: str
    regionCode3: str
    regionName3: str

    @staticmethod
    def from_dict(obj: Any) -> "RegionList":
        _cafeId = int(obj.get("cafeId"))
        _articleId = int(obj.get("articleId"))
        _regionCode1 = str(obj.get("regionCode1"))
        _regionName1 = str(obj.get("regionName1"))
        _regionCode2 = str(obj.get("regionCode2"))
        _regionName2 = str(obj.get("regionName2"))
        _regionCode3 = str(obj.get("regionCode3"))
        _regionName3 = str(obj.get("regionName3"))
        return RegionList(
            _cafeId,
            _articleId,
            _regionCode1,
            _regionName1,
            _regionCode2,
            _regionName2,
            _regionCode3,
            _regionName3,
        )


@dataclass
class Result:
    highlightOff: bool
    cafeId: int
    totalArticleCount: int
    articleCount: int
    perPage: int
    page: int
    showSuicideSaver: bool
    query: str
    searchBy: int
    sortBy: str
    articleList: List[ArticleList]
    memoSearch: bool
    lastPage: bool

    @staticmethod
    def from_dict(obj: Any) -> "Result":
        _highlightOff = obj.get("highlightOff")
        _cafeId = int(obj.get("cafeId"))
        _totalArticleCount = int(obj.get("totalArticleCount"))
        _articleCount = int(obj.get("articleCount"))
        _perPage = int(obj.get("perPage"))
        _page = int(obj.get("page"))
        _showSuicideSaver = obj.get("showSuicideSaver")
        _query = str(obj.get("query"))
        _searchBy = int(obj.get("searchBy"))
        _sortBy = str(obj.get("sortBy"))
        _articleList = [ArticleList.from_dict(y) for y in obj.get("articleList")]
        _memoSearch = obj.get("memoSearch")
        _lastPage = obj.get("lastPage")
        return Result(
            _highlightOff,
            _cafeId,
            _totalArticleCount,
            _articleCount,
            _perPage,
            _page,
            _showSuicideSaver,
            _query,
            _searchBy,
            _sortBy,
            _articleList,
            _memoSearch,
            _lastPage,
        )


@dataclass
class BoardSearchRoot:
    message: Message

    @staticmethod
    def from_dict(obj: Any) -> "BoardSearchRoot":
        _message = Message.from_dict(obj.get("message"))
        return BoardSearchRoot(_message)
