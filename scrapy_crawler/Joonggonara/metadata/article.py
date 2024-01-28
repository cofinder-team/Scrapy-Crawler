from dataclasses import dataclass
from typing import Any, List


@dataclass
class Alarm:
    isShow: bool
    isChecked: bool

    @staticmethod
    def from_dict(obj: Any) -> "Alarm":
        _isShow = obj.get("isShow")
        _isChecked = obj.get("isChecked")
        return Alarm(_isShow, _isChecked)


@dataclass
class Article:
    id: int
    refArticleId: int
    menu: "Menu"
    subject: str
    writer: "Writer"
    subscribeWriter: "SubscribeWriter"
    writeDate: int
    readCount: int
    commentCount: int
    existScrapAddContent: bool
    contentHtml: str
    customElements: List[object]
    gdid: str
    replyListOrder: str
    isNotice: bool
    isNewComment: bool
    isDeleteParent: bool
    isMarket: bool
    isGroupPurchase: bool
    isPersonalTrade: bool
    isReadable: bool
    isBlind: bool
    isOpen: bool
    isEnableScrap: bool
    scrapCount: int
    isEnableExternal: bool
    isEnableSocialPlugin: bool
    isWriteComment: bool
    isAutoSourcing: bool

    @staticmethod
    def from_dict(obj: Any) -> "Article":
        _id = int(obj.get("id"))
        _refArticleId = int(obj.get("refArticleId"))
        _menu = Menu.from_dict(obj.get("menu"))
        _subject = str(obj.get("subject"))
        _writer = Writer.from_dict(obj.get("writer"))
        _subscribeWriter = SubscribeWriter.from_dict(obj.get("subscribeWriter"))
        _writeDate = int(obj.get("writeDate"))
        _readCount = int(obj.get("readCount"))
        _commentCount = int(obj.get("commentCount"))
        _existScrapAddContent = obj.get("existScrapAddContent")
        _contentHtml = str(obj.get("contentHtml"))
        _customElements = [y for y in obj.get("customElements")]
        _gdid = str(obj.get("gdid"))
        _replyListOrder = str(obj.get("replyListOrder"))
        _isNotice = obj.get("isNotice")
        _isNewComment = obj.get("isNewComment")
        _isDeleteParent = obj.get("isDeleteParent")
        _isMarket = obj.get("isMarket")
        _isGroupPurchase = obj.get("isGroupPurchase")
        _isPersonalTrade = obj.get("isPersonalTrade")
        _isReadable = obj.get("isReadable")
        _isBlind = obj.get("isBlind")
        _isOpen = obj.get("isOpen")
        _isEnableScrap = obj.get("isEnableScrap")
        _scrapCount = int(obj.get("scrapCount"))
        _isEnableExternal = obj.get("isEnableExternal")
        _isEnableSocialPlugin = obj.get("isEnableSocialPlugin")
        _isWriteComment = obj.get("isWriteComment")
        _isAutoSourcing = obj.get("isAutoSourcing")
        return Article(
            _id,
            _refArticleId,
            _menu,
            _subject,
            _writer,
            _subscribeWriter,
            _writeDate,
            _readCount,
            _commentCount,
            _existScrapAddContent,
            _contentHtml,
            _customElements,
            _gdid,
            _replyListOrder,
            _isNotice,
            _isNewComment,
            _isDeleteParent,
            _isMarket,
            _isGroupPurchase,
            _isPersonalTrade,
            _isReadable,
            _isBlind,
            _isOpen,
            _isEnableScrap,
            _scrapCount,
            _isEnableExternal,
            _isEnableSocialPlugin,
            _isWriteComment,
            _isAutoSourcing,
        )


@dataclass
class ArticleRegion:
    rcode: str
    type: str
    name: str
    regionCode1: str
    regionName1: str
    regionCode2: str
    regionName2: str
    regionCode3: str
    regionName3: str

    @staticmethod
    def from_dict(obj: Any) -> "ArticleRegion":
        _rcode = str(obj.get("rcode"))
        _type = str(obj.get("type"))
        _name = str(obj.get("name"))
        _regionCode1 = str(obj.get("regionCode1"))
        _regionName1 = str(obj.get("regionName1"))
        _regionCode2 = str(obj.get("regionCode2"))
        _regionName2 = str(obj.get("regionName2"))
        _regionCode3 = str(obj.get("regionCode3"))
        _regionName3 = str(obj.get("regionName3"))
        return ArticleRegion(
            _rcode,
            _type,
            _name,
            _regionCode1,
            _regionName1,
            _regionCode2,
            _regionName2,
            _regionCode3,
            _regionName3,
        )


@dataclass
class Comments:
    items: List[object]
    alarm: Alarm
    disableWriteReason: str

    @staticmethod
    def from_dict(obj: Any) -> "Comments":
        _items = [y for y in obj.get("items")]
        _alarm = Alarm.from_dict(obj.get("alarm"))
        _disableWriteReason = str(obj.get("disableWriteReason"))
        return Comments(_items, _alarm, _disableWriteReason)


@dataclass
class EmotionSatisfactionStat:
    bestCount: int
    goodCount: int
    sorryCount: int

    @staticmethod
    def from_dict(obj: Any) -> "EmotionSatisfactionStat":
        _bestCount = int(obj.get("bestCount"))
        _goodCount = int(obj.get("goodCount"))
        _sorryCount = int(obj.get("sorryCount"))
        return EmotionSatisfactionStat(_bestCount, _goodCount, _sorryCount)


@dataclass
class Image:
    url: str

    @staticmethod
    def from_dict(obj: Any) -> "Image":
        _url = str(obj.get("url"))
        return Image(_url)


@dataclass
class Menu:
    id: int
    name: str
    menuType: str
    boardType: str
    badMenu: bool
    badMenuByRestrict: bool

    @staticmethod
    def from_dict(obj: Any) -> "Menu":
        _id = int(obj.get("id"))
        _name = str(obj.get("name"))
        _menuType = str(obj.get("menuType"))
        _boardType = str(obj.get("boardType"))
        _badMenu = obj.get("badMenu")
        _badMenuByRestrict = obj.get("badMenuByRestrict")
        return Menu(_id, _name, _menuType, _boardType, _badMenu, _badMenuByRestrict)


@dataclass
class Permission:
    isBoardStaff: bool
    isOnlyOptionalBoardStaff: bool
    isActivityStopExecutable: bool
    isNoticeRegistrable: bool
    isViceManager: bool
    isCafeManager: bool
    isEntireBoardStaff: bool
    isMemberStaff: bool

    @staticmethod
    def from_dict(obj: Any) -> "Permission":
        _isBoardStaff = obj.get("isBoardStaff")
        _isOnlyOptionalBoardStaff = obj.get("isOnlyOptionalBoardStaff")
        _isActivityStopExecutable = obj.get("isActivityStopExecutable")
        _isNoticeRegistrable = obj.get("isNoticeRegistrable")
        _isViceManager = obj.get("isViceManager")
        _isCafeManager = obj.get("isCafeManager")
        _isEntireBoardStaff = obj.get("isEntireBoardStaff")
        _isMemberStaff = obj.get("isMemberStaff")
        return Permission(
            _isBoardStaff,
            _isOnlyOptionalBoardStaff,
            _isActivityStopExecutable,
            _isNoticeRegistrable,
            _isViceManager,
            _isCafeManager,
            _isEntireBoardStaff,
            _isMemberStaff,
        )


@dataclass
class ReadOnlyModeInfo:
    readOnlyModeStatus: bool
    timeToPreNotice: bool
    timeToNotice: bool
    emergency: bool
    readOnlyNoticeDuration: str
    linkToNoticeURL: str

    @staticmethod
    def from_dict(obj: Any) -> "ReadOnlyModeInfo":
        _readOnlyModeStatus = obj.get("readOnlyModeStatus")
        _timeToPreNotice = obj.get("timeToPreNotice")
        _timeToNotice = obj.get("timeToNotice")
        _emergency = obj.get("emergency")
        _readOnlyNoticeDuration = str(obj.get("readOnlyNoticeDuration"))
        _linkToNoticeURL = str(obj.get("linkToNoticeURL"))
        return ReadOnlyModeInfo(
            _readOnlyModeStatus,
            _timeToPreNotice,
            _timeToNotice,
            _emergency,
            _readOnlyNoticeDuration,
            _linkToNoticeURL,
        )


@dataclass
class Region:
    regionCode1: str
    regionName1: str
    regionCode2: str
    regionName2: str
    regionCode3: str
    regionName3: str

    @staticmethod
    def from_dict(obj: Any) -> "Region":
        _regionCode1 = str(obj.get("regionCode1"))
        _regionName1 = str(obj.get("regionName1"))
        _regionCode2 = str(obj.get("regionCode2"))
        _regionName2 = str(obj.get("regionName2"))
        _regionCode3 = str(obj.get("regionCode3"))
        _regionName3 = str(obj.get("regionName3"))
        return Region(
            _regionCode1,
            _regionName1,
            _regionCode2,
            _regionName2,
            _regionCode3,
            _regionName3,
        )


@dataclass
class Result:
    cafeId: int
    articleId: int
    heads: List[object]
    article: Article
    comments: Comments
    user: "User"
    attaches: List[object]
    tags: List[object]
    saleInfo: "SaleInfo"
    editorVersion: str
    articleRegion: ArticleRegion
    reviewPersonalStat: "ReviewPersonalStat"
    commAdSupport: bool
    isReadOnlyMode: bool
    isW800: bool

    @staticmethod
    def from_dict(obj: Any) -> "Result":
        _cafeId = int(obj.get("cafeId"))
        _articleId = int(obj.get("articleId"))
        _heads = [y for y in obj.get("heads")]
        _article = Article.from_dict(obj.get("article"))
        _comments = Comments.from_dict(obj.get("comments"))
        _user = User.from_dict(obj.get("user"))
        _attaches = [y for y in obj.get("attaches")]
        _tags = [y for y in obj.get("tags")]
        _saleInfo = SaleInfo.from_dict(obj.get("saleInfo"))
        _editorVersion = str(obj.get("editorVersion"))
        _articleRegion = ArticleRegion.from_dict(obj.get("articleRegion"))
        _reviewPersonalStat = ReviewPersonalStat.from_dict(
            obj.get("reviewPersonalStat")
        )
        _commAdSupport = obj.get("commAdSupport")
        _isReadOnlyMode = obj.get("isReadOnlyMode")
        _isW800 = obj.get("isW800")
        return Result(
            _cafeId,
            _articleId,
            _heads,
            _article,
            _comments,
            _user,
            _attaches,
            _tags,
            _saleInfo,
            _editorVersion,
            _articleRegion,
            _reviewPersonalStat,
            _commAdSupport,
            _isReadOnlyMode,
            _isW800,
        )


@dataclass
class ReviewPersonalStat:
    emotionSatisfactionStat: EmotionSatisfactionStat

    @staticmethod
    def from_dict(obj: Any) -> "ReviewPersonalStat":
        _emotionSatisfactionStat = EmotionSatisfactionStat.from_dict(
            obj.get("emotionSatisfactionStat")
        )
        return ReviewPersonalStat(_emotionSatisfactionStat)


@dataclass
class ArticleRoot:
    result: Result

    @staticmethod
    def from_dict(obj: Any) -> "ArticleRoot":
        _result = Result.from_dict(obj.get("result"))
        return ArticleRoot(_result)


@dataclass
class SaleInfo:
    type: str
    imgUrl: str
    saleStatus: str
    productName: str
    price: int
    verifiedSeller: bool
    deliveryMethod: str
    email: str
    category1: str
    category1Name: str
    category2: str
    category2Name: str
    category3: str
    category3Name: str
    productCondition: str
    deliveryTypes: List[str]
    regions: List[Region]
    image: Image
    isShowRedcardWarning: bool
    isPhoneAvailable: bool
    isWrittenAbroad: bool
    isNpayRemit: bool
    isOnSale: bool
    isUseSafetyPayment: bool
    isExperienceMode: bool
    isAgreeOpenPhoneNo: bool
    isUseOtn: bool
    isExpireSafetyPayment: bool
    isPersonalTrade: bool
    isStoreFarmProduct: bool
    isFailToLoadStoreFarmProduct: bool
    isShowPurchaseButton: bool

    @staticmethod
    def from_dict(obj: Any) -> "SaleInfo":
        _type = str(obj.get("type"))
        _imgUrl = str(obj.get("imgUrl"))
        _saleStatus = str(obj.get("saleStatus"))
        _productName = str(obj.get("productName"))
        _price = int(obj.get("price"))
        _verifiedSeller = obj.get("verifiedSeller")
        _deliveryMethod = str(obj.get("deliveryMethod"))
        _email = str(obj.get("email"))
        _category1 = str(obj.get("category1"))
        _category1Name = str(obj.get("category1Name"))
        _category2 = str(obj.get("category2"))
        _category2Name = str(obj.get("category2Name"))
        _category3 = str(obj.get("category3"))
        _category3Name = str(obj.get("category3Name"))
        _productCondition = str(obj.get("productCondition"))
        _deliveryTypes = [y for y in obj.get("deliveryTypes")]
        _regions = [Region.from_dict(y) for y in obj.get("regions")]
        _image = Image.from_dict(obj.get("image"))
        _isShowRedcardWarning = obj.get("isShowRedcardWarning")
        _isPhoneAvailable = obj.get("isPhoneAvailable")
        _isWrittenAbroad = obj.get("isWrittenAbroad")
        _isNpayRemit = obj.get("isNpayRemit")
        _isOnSale = obj.get("isOnSale")
        _isUseSafetyPayment = obj.get("isUseSafetyPayment")
        _isExperienceMode = obj.get("isExperienceMode")
        _isAgreeOpenPhoneNo = obj.get("isAgreeOpenPhoneNo")
        _isUseOtn = obj.get("isUseOtn")
        _isExpireSafetyPayment = obj.get("isExpireSafetyPayment")
        _isPersonalTrade = obj.get("isPersonalTrade")
        _isStoreFarmProduct = obj.get("isStoreFarmProduct")
        _isFailToLoadStoreFarmProduct = obj.get("isFailToLoadStoreFarmProduct")
        _isShowPurchaseButton = obj.get("isShowPurchaseButton")
        return SaleInfo(
            _type,
            _imgUrl,
            _saleStatus,
            _productName,
            _price,
            _verifiedSeller,
            _deliveryMethod,
            _email,
            _category1,
            _category1Name,
            _category2,
            _category2Name,
            _category3,
            _category3Name,
            _productCondition,
            _deliveryTypes,
            _regions,
            _image,
            _isShowRedcardWarning,
            _isPhoneAvailable,
            _isWrittenAbroad,
            _isNpayRemit,
            _isOnSale,
            _isUseSafetyPayment,
            _isExperienceMode,
            _isAgreeOpenPhoneNo,
            _isUseOtn,
            _isExpireSafetyPayment,
            _isPersonalTrade,
            _isStoreFarmProduct,
            _isFailToLoadStoreFarmProduct,
            _isShowPurchaseButton,
        )


@dataclass
class SubscribeWriter:
    subscribe: bool
    push: bool

    @staticmethod
    def from_dict(obj: Any) -> "SubscribeWriter":
        _subscribe = obj.get("subscribe")
        _push = obj.get("push")
        return SubscribeWriter(_subscribe, _push)


@dataclass
class User:
    memberKey: str
    baMemberKey: str
    nick: str
    memberLevel: int
    blockMemberKeyList: List[object]
    memberLevelName: str
    memberLevelIconUrl: str
    appliedAlready: bool
    permission: Permission
    currentPopularMember: bool
    isCafeMember: bool
    isLogin: bool
    isOwner: bool
    isGroupId: bool
    isBelowAge14: bool

    @staticmethod
    def from_dict(obj: Any) -> "User":
        _memberKey = str(obj.get("memberKey"))
        _baMemberKey = str(obj.get("baMemberKey"))
        _nick = str(obj.get("nick"))
        _memberLevel = int(obj.get("memberLevel"))
        _blockMemberKeyList = [y for y in obj.get("blockMemberKeyList")]
        _memberLevelName = str(obj.get("memberLevelName"))
        _memberLevelIconUrl = str(obj.get("memberLevelIconUrl"))
        _appliedAlready = obj.get("appliedAlready")
        _permission = Permission.from_dict(obj.get("permission"))
        _currentPopularMember = obj.get("currentPopularMember")
        _isCafeMember = obj.get("isCafeMember")
        _isLogin = obj.get("isLogin")
        _isOwner = obj.get("isOwner")
        _isGroupId = obj.get("isGroupId")
        _isBelowAge14 = obj.get("isBelowAge14")
        return User(
            _memberKey,
            _baMemberKey,
            _nick,
            _memberLevel,
            _blockMemberKeyList,
            _memberLevelName,
            _memberLevelIconUrl,
            _appliedAlready,
            _permission,
            _currentPopularMember,
            _isCafeMember,
            _isLogin,
            _isOwner,
            _isGroupId,
            _isBelowAge14,
        )


@dataclass
class Writer:
    id: str
    memberKey: str
    baMemberKey: str
    nick: str
    image: Image
    memberLevel: int
    memberLevelName: str
    memberLevelIconUrl: str
    currentPopularMember: bool

    @staticmethod
    def from_dict(obj: Any) -> "Writer":
        _id = str(obj.get("id"))
        _memberKey = str(obj.get("memberKey"))
        _baMemberKey = str(obj.get("baMemberKey"))
        _nick = str(obj.get("nick"))
        _image = Image.from_dict(obj.get("image"))
        _memberLevel = int(obj.get("memberLevel")) if obj.get("memberLevel") else 0
        _memberLevelName = str(obj.get("memberLevelName"))
        _memberLevelIconUrl = str(obj.get("memberLevelIconUrl"))
        _currentPopularMember = obj.get("currentPopularMember")
        return Writer(
            _id,
            _memberKey,
            _baMemberKey,
            _nick,
            _image,
            _memberLevel,
            _memberLevelName,
            _memberLevelIconUrl,
            _currentPopularMember,
        )
