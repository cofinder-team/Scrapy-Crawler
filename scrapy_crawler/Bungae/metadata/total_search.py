from dataclasses import dataclass
from typing import Any, List


@dataclass
class Filters:
    q: str
    page: str

    @staticmethod
    def from_dict(obj: Any) -> "Filters":
        _q = str(obj.get("q"))
        _page = str(obj.get("page"))
        return Filters(_q, _page)


@dataclass
class Flag:
    type: str
    label: str
    event_type: str

    @staticmethod
    def from_dict(obj: Any) -> "Flag":
        _type = str(obj.get("type"))
        _label = str(obj.get("label"))
        _event_type = str(obj.get("event_type"))
        return Flag(_type, _label, _event_type)


@dataclass
class BgList:
    pid: str
    name: str
    price: str
    product_image: str
    status: str
    ad: bool
    inspection: str
    bun_pay_filter_enabled: bool
    care: bool
    location: str
    badges: List[str]
    bizseller: bool
    checkout: bool
    contact_hope: bool
    free_shipping: bool
    is_adult: bool
    num_comment: str
    num_faved: str
    only_neighborhood: bool
    outlink_url: str
    style: str
    tag: str
    uid: str
    update_time: int
    used: int
    proshop: bool
    category_id: str
    ref_content: str
    ref_source: str
    imp_id: str
    ad_ref: str
    faved: bool

    @staticmethod
    def from_dict(obj: Any) -> "BgList":
        _pid = str(obj.get("pid"))
        _name = str(obj.get("name"))
        _price = str(obj.get("price"))
        _product_image = str(obj.get("product_image"))
        _status = str(obj.get("status"))
        _ad = obj.get("ad")
        _inspection = str(obj.get("inspection"))
        _bun_pay_filter_enabled = obj.get("bun_pay_filter_enabled")
        _care = obj.get("care")
        _location = str(obj.get("location"))
        _badges = [y for y in obj.get("badges")]
        _bizseller = obj.get("bizseller")
        _checkout = obj.get("checkout")
        _contact_hope = obj.get("contact_hope")
        _free_shipping = obj.get("free_shipping")
        _is_adult = obj.get("is_adult")
        _num_comment = str(obj.get("num_comment"))
        _num_faved = str(obj.get("num_faved"))
        _only_neighborhood = obj.get("only_neighborhood")
        _outlink_url = str(obj.get("outlink_url"))
        _style = str(obj.get("style"))
        _tag = str(obj.get("tag"))
        _uid = str(obj.get("uid"))
        _update_time = int(obj.get("update_time"))
        _used = int(obj.get("used"))
        _proshop = obj.get("proshop")
        _category_id = str(obj.get("category_id"))
        _ref_content = str(obj.get("ref_content"))
        _ref_source = str(obj.get("ref_source"))
        _imp_id = str(obj.get("imp_id"))
        _ad_ref = str(obj.get("ad_ref"))
        _faved = obj.get("faved")
        return BgList(
            _pid,
            _name,
            _price,
            _product_image,
            _status,
            _ad,
            _inspection,
            _bun_pay_filter_enabled,
            _care,
            _location,
            _badges,
            _bizseller,
            _checkout,
            _contact_hope,
            _free_shipping,
            _is_adult,
            _num_comment,
            _num_faved,
            _only_neighborhood,
            _outlink_url,
            _style,
            _tag,
            _uid,
            _update_time,
            _used,
            _proshop,
            _category_id,
            _ref_content,
            _ref_source,
            _imp_id,
            _ad_ref,
            _faved,
        )


@dataclass
class TotalSearchRoot:
    result: str
    list: List[BgList]
    filters: Filters
    n: int
    num_found: int
    view_type: str
    flags: List[Flag]

    @staticmethod
    def from_dict(obj: Any) -> "TotalSearchRoot":
        _result = str(obj.get("result"))
        _list = [BgList.from_dict(y) for y in obj.get("list")]
        _filters = Filters.from_dict(obj.get("filters"))
        _n = int(obj.get("n"))
        _num_found = int(obj.get("num_found"))
        _view_type = str(obj.get("view_type"))
        _flags = [Flag.from_dict(y) for y in obj.get("flags")]
        return TotalSearchRoot(
            _result, _list, _filters, _n, _num_found, _view_type, _flags
        )
