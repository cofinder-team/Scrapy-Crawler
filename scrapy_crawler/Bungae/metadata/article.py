from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class Attribute:
    typography: str
    color: str
    style: str

    @staticmethod
    def from_dict(obj: Any) -> "Attribute":
        _typography = str(obj.get("typography"))
        _color = str(obj.get("color"))
        _style = str(obj.get("style"))
        return Attribute(_typography, _color, _style)


@dataclass
class Benefit:
    title: str
    contents: List["Content"]
    moreContents: List["MoreContent"]

    @staticmethod
    def from_dict(obj: Any) -> "Benefit":
        _title = str(obj.get("title"))
        _contents = (
            [Content.from_dict(y) for y in obj.get("contents")]
            if obj.get("contents")
            else []
        )
        _moreContents = (
            [MoreContent.from_dict(y) for y in obj.get("moreContents")]
            if obj.get("moreContents")
            else []
        )
        return Benefit(_title, _contents, _moreContents)


@dataclass
class Brand:
    id: int
    name: str
    imageUrl: str

    @staticmethod
    def from_dict(obj: Any) -> Optional["Brand"]:
        if obj is None:
            return None
        _id = int(obj.get("id"))
        _name = str(obj.get("name"))
        _imageUrl = str(obj.get("imageUrl"))
        return Brand(_id, _name, _imageUrl)


@dataclass
class Bunpay:
    enabled: bool
    shipping: bool
    inPerson: bool

    @staticmethod
    def from_dict(obj: Any) -> "Bunpay":
        _enabled = obj.get("enabled")
        _shipping = obj.get("shipping")
        _inPerson = obj.get("inPerson")
        return Bunpay(_enabled, _shipping, _inPerson)


@dataclass
class Category:
    id: str
    name: str
    imageUrl: str

    @staticmethod
    def from_dict(obj: Any) -> "Category":
        _id = str(obj.get("id"))
        _name = str(obj.get("name"))
        _imageUrl = str(obj.get("imageUrl"))
        return Category(_id, _name, _imageUrl)


@dataclass
class Content:
    text: "Text"
    iconUrl: str
    appUrl: str

    @staticmethod
    def from_dict(obj: Any) -> "Content":
        _text = Text.from_dict(obj.get("text"))
        _iconUrl = str(obj.get("iconUrl"))
        _appUrl = str(obj.get("appUrl"))
        return Content(_text, _iconUrl, _appUrl)


@dataclass
class Data:
    product: "Product"
    banners: List[object]
    bunpay: Bunpay
    benefits: List[Benefit]
    shop: "Shop"
    shopProductCount: int
    shopProducts: List["ShopProduct"]
    reportUrl: str

    @staticmethod
    def from_dict(obj: Any) -> "Data":
        _product = Product.from_dict(obj.get("product"))
        _banners = [y for y in obj.get("banners")] if obj.get("banners") else []
        _bunpay = Bunpay.from_dict(obj.get("bunpay"))
        _benefits = (
            [Benefit.from_dict(y) for y in obj.get("benefits")]
            if obj.get("benefits")
            else []
        )
        _shop = Shop.from_dict(obj.get("shop"))
        _shopProductCount = int(obj.get("shopProductCount"))
        _shopProducts = (
            [ShopProduct.from_dict(y) for y in obj.get("shopProducts")]
            if obj.get("shopProducts")
            else []
        )
        _reportUrl = str(obj.get("reportUrl"))
        return Data(
            _product,
            _banners,
            _bunpay,
            _benefits,
            _shop,
            _shopProductCount,
            _shopProducts,
            _reportUrl,
        )


@dataclass
class Geo:
    lat: Optional[float]
    lon: Optional[float]
    address: Optional[str]
    label: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> Optional["Geo"]:
        if obj is None:
            return None
        _lat = float(obj.get("lat")) if obj.get("lat") else None
        _lon = float(obj.get("lon")) if obj.get("lon") else None
        _address = str(obj.get("address")) if obj.get("address") else None
        _label = str(obj.get("label")) if obj.get("label") else None
        return Geo(_lat, _lon, _address, _label)


@dataclass
class KeywordLink:
    keyword: str
    appUrl: str
    imageUrl: str
    emphasis: bool

    @staticmethod
    def from_dict(obj: Any) -> "KeywordLink":
        _keyword = str(obj.get("keyword"))
        _appUrl = str(obj.get("appUrl"))
        _imageUrl = str(obj.get("imageUrl"))
        _emphasis = obj.get("emphasis")
        return KeywordLink(_keyword, _appUrl, _imageUrl, _emphasis)


@dataclass
class Main:
    text: str
    attribute: Attribute

    @staticmethod
    def from_dict(obj: Any) -> "Main":
        _text = str(obj.get("text"))
        _attribute = Attribute.from_dict(obj.get("attribute"))
        return Main(_text, _attribute)


@dataclass
class Metrics:
    favoriteCount: int
    buntalkCount: int
    viewCount: int
    commentCount: int

    @staticmethod
    def from_dict(obj: Any) -> "Metrics":
        _favoriteCount = int(obj.get("favoriteCount"))
        _buntalkCount = int(obj.get("buntalkCount"))
        _viewCount = int(obj.get("viewCount"))
        _commentCount = int(obj.get("commentCount"))
        return Metrics(_favoriteCount, _buntalkCount, _viewCount, _commentCount)


@dataclass
class MoreContent:
    text: "Text"
    iconUrl: str
    appUrl: str

    @staticmethod
    def from_dict(obj: Any) -> "MoreContent":
        _text = Text.from_dict(obj.get("text"))
        _iconUrl = str(obj.get("iconUrl"))
        _appUrl = str(obj.get("appUrl"))
        return MoreContent(_text, _iconUrl, _appUrl)


@dataclass
class Product:
    pid: int
    name: str
    description: str
    price: int
    qty: int
    includeShippingCost: bool
    exchangeable: bool
    ad: bool
    saleStatus: str
    status: str
    keywords: List[str]
    imageUrl: str
    imageCount: int
    bunpayHope: bool
    geo: Optional[Geo]
    metrics: Metrics
    category: Category
    brand: Optional[Brand]
    inspectionStatus: str
    updatedAt: str
    updatedBefore: str
    keywordLinks: List[KeywordLink]
    exportNaverShopping: bool
    showNaverShoppingLabel: bool
    care: bool
    specLabels: List["SpecLabel"]

    @staticmethod
    def from_dict(obj: Any) -> "Product":
        _pid = int(obj.get("pid"))
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _price = int(obj.get("price"))
        _qty = int(obj.get("qty"))
        _includeShippingCost = obj.get("includeShippingCost")
        _exchangeable = obj.get("exchangeable")
        _ad = obj.get("ad")
        _saleStatus = str(obj.get("saleStatus"))
        _status = str(obj.get("status"))
        _keywords = [y for y in obj.get("keywords")] if obj.get("keywords") else []
        _imageUrl = str(obj.get("imageUrl"))
        _imageCount = int(obj.get("imageCount"))
        _bunpayHope = obj.get("bunpayHope")
        _geo = Geo.from_dict(obj.get("geo"))
        _metrics = Metrics.from_dict(obj.get("metrics"))
        _category = Category.from_dict(obj.get("category"))
        _brand = Brand.from_dict(obj.get("brand"))
        _inspectionStatus = str(obj.get("inspectionStatus"))
        _updatedAt = str(obj.get("updatedAt"))
        _updatedBefore = str(obj.get("updatedBefore"))
        _keywordLinks = (
            [KeywordLink.from_dict(y) for y in obj.get("keywordLinks")]
            if obj.get("keywordLinks")
            else []
        )
        _exportNaverShopping = obj.get("exportNaverShopping")
        _showNaverShoppingLabel = obj.get("showNaverShoppingLabel")
        _care = obj.get("care")
        _specLabels = (
            [SpecLabel.from_dict(y) for y in obj.get("specLabels")]
            if obj.get("specLabels")
            else []
        )
        return Product(
            _pid,
            _name,
            _description,
            _price,
            _qty,
            _includeShippingCost,
            _exchangeable,
            _ad,
            _saleStatus,
            _status,
            _keywords,
            _imageUrl,
            _imageCount,
            _bunpayHope,
            _geo,
            _metrics,
            _category,
            _brand,
            _inspectionStatus,
            _updatedAt,
            _updatedBefore,
            _keywordLinks,
            _exportNaverShopping,
            _showNaverShoppingLabel,
            _care,
            _specLabels,
        )


@dataclass
class Proshop:
    isProshop: bool
    isRestrictedCandidate: bool

    @staticmethod
    def from_dict(obj: Any) -> "Proshop":
        _isProshop = obj.get("isProshop")
        _isRestrictedCandidate = obj.get("isRestrictedCandidate")
        return Proshop(_isProshop, _isRestrictedCandidate)


@dataclass
class ArticleRoot:
    data: Data

    @staticmethod
    def from_dict(obj: Any) -> "ArticleRoot":
        _data = Data.from_dict(obj.get("data"))
        return ArticleRoot(_data)


@dataclass
class Shop:
    uid: int
    name: str
    imageUrl: str
    badgeUrl: str
    grade: int
    followerCount: int
    isIdentified: bool
    proshop: Proshop
    joinDate: str

    @staticmethod
    def from_dict(obj: Any) -> "Shop":
        _uid = int(obj.get("uid"))
        _name = str(obj.get("name"))
        _imageUrl = str(obj.get("imageUrl"))
        _badgeUrl = str(obj.get("badgeUrl"))
        _grade = int(obj.get("grade"))
        _followerCount = int(obj.get("followerCount"))
        _isIdentified = obj.get("isIdentified")
        _proshop = Proshop.from_dict(obj.get("proshop"))
        _joinDate = str(obj.get("joinDate"))
        return Shop(
            _uid,
            _name,
            _imageUrl,
            _badgeUrl,
            _grade,
            _followerCount,
            _isIdentified,
            _proshop,
            _joinDate,
        )


@dataclass
class ShopProduct:
    pid: int
    name: str
    price: int
    bunpayHope: bool
    badges: List[object]
    firstImageUrl: str
    inspectionStatus: str
    care: bool

    @staticmethod
    def from_dict(obj: Any) -> "ShopProduct":
        _pid = int(obj.get("pid"))
        _name = str(obj.get("name"))
        _price = int(obj.get("price"))
        _bunpayHope = obj.get("bunpayHope")
        _badges = [y for y in obj.get("badges")] if obj.get("badges") else []
        _firstImageUrl = str(obj.get("firstImageUrl"))
        _inspectionStatus = str(obj.get("inspectionStatus"))
        _care = obj.get("care")
        return ShopProduct(
            _pid,
            _name,
            _price,
            _bunpayHope,
            _badges,
            _firstImageUrl,
            _inspectionStatus,
            _care,
        )


@dataclass
class SpecLabel:
    label: str
    emphasis: bool

    @staticmethod
    def from_dict(obj: Any) -> "SpecLabel":
        _label = str(obj.get("label"))
        _emphasis = obj.get("emphasis")
        return SpecLabel(_label, _emphasis)


@dataclass
class Sub:
    text: str
    attribute: Attribute
    key: str

    @staticmethod
    def from_dict(obj: Any) -> "Sub":
        _text = str(obj.get("text"))
        _attribute = Attribute.from_dict(obj.get("attribute"))
        _key = str(obj.get("key"))
        return Sub(_text, _attribute, _key)


@dataclass
class Text:
    main: Main
    sub: List[Sub]

    @staticmethod
    def from_dict(obj: Any) -> "Text":
        _main = Main.from_dict(obj.get("main"))
        _sub = [Sub.from_dict(y) for y in obj.get("sub")] if obj.get("sub") else []
        return Text(_main, _sub)
