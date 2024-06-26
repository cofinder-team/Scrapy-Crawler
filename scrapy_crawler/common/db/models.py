import datetime
from typing import Any

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base: Any = declarative_base()


class RawUsedItem(Base):
    __tablename__ = "raw_used_item"
    id = Column(Integer, primary_key=True)
    writer = Column("writer", String)
    title = Column("title", String)
    content = Column("content", String)
    price = Column("price", Integer)
    date = Column("date", String)
    url = Column("url", String)
    img_url = Column("img_url", String)
    source = Column("source", String)
    type = Column("type", ForeignKey("item.type"))
    item_id = Column("item_id", ForeignKey("item.id"))
    image = Column("image", LargeBinary)
    classified = Column("classified", Boolean, default=False)
    unused = Column("unused", Boolean, default=False)
    raw_json = Column("raw_json", JSONB)


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    type = Column("type", String, primary_key=True)


class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, primary_key=True)
    type = Column("type", Boolean, primary_key=True)
    name = Column("name", String)


class ItemMacbook(Base):
    __tablename__ = "item_macbook"
    id = Column(Integer, primary_key=True)
    type = Column("type", ForeignKey("item.type"))
    model = Column("model", ForeignKey("model.type"))
    option = Column("option", Integer)
    chip = Column("chip", String)
    cpu_core = Column("cpu", Integer)
    gpu_core = Column("gpu", Integer)
    ram = Column("ram", Integer)
    ssd = Column("ssd", Integer)


class Deal(Base):
    def __repr__(self):
        return (
            f"<Deal(id={self.id}, type={self.type}, "
            f"item_id={self.item_id}, price={self.price}, unused={self.unused}>"
        )

    __tablename__ = "deal"
    id = Column(Integer, primary_key=True)
    type = Column("type", ForeignKey("item.type"))
    item_id = Column("item_id", ForeignKey("item.id"))
    price = Column("price", Integer)
    sold = Column("sold", Boolean, default=False)
    unused = Column("unused", Boolean, default=False)
    source = Column("source", String)
    url = Column("url", String)
    image = Column("image", LargeBinary)
    date = Column("date", String)
    last_crawled = Column(
        "last_crawled",
        String,
        default=(datetime.datetime.now() + datetime.timedelta(hours=9)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )
    writer = Column("writer", String)
    title = Column("title", String)
    content = Column("content", String)
    apple_care = Column("apple_care", Boolean)
    deleted_at = Column("deleted_at", String)
    condition = Column("condition", Enum("U", "S", "A"))


class Trade(Base):
    __tablename__ = "trade"
    id = Column(Integer, primary_key=True)
    type = Column("type", ForeignKey("item.type"))
    item_id = Column("item_id", ForeignKey("item.id"))
    date = Column("date", String)
    price = Column("price", Integer)
    unused = Column("unused", Boolean, default=False)
    care = Column("care", Boolean, default=False)
    source = Column("source", String)
    url = Column("url", String)
    title = Column("title", String)
    content = Column("content", String)
    writer = Column("writer", String)


class ItemIpad(Base):
    __tablename__ = "item_ipad"
    id = Column(Integer, primary_key=True)
    type = Column("type", ForeignKey("item.type"))
    model = Column("model", ForeignKey("model.type"))
    option = Column("option", Integer)
    generation = Column("gen", Integer)
    ssd = Column("storage", Integer)
    cellular = Column("cellular", Boolean)


class ItemIphone(Base):
    __tablename__ = "item_iphone"
    id = Column(Integer, primary_key=True)
    type = Column("type", ForeignKey("item.type"))
    model = Column("model", ForeignKey("model.type"))
    option = Column("option", Integer)
    model_suffix = Column("model_suffix", String)
    ssd = Column("storage", Integer)


class ViewTrade(Base):
    __tablename__ = "price_trade"
    type = Column("type", String, primary_key=True)
    id = Column("id", Integer)
    unused = Column("unused", Boolean)
    source = Column("source", String)
    date = Column("date", String)
    average = Column("average", Integer)
    price_20 = Column("price_20", Integer)
    price_80 = Column("price_80", Integer)
    cnt = Column("cnt", Integer)


class DroppedItem(Base):
    __tablename__ = "dropped_item"
    id = Column(Integer, primary_key=True)
    category = Column("category", String)
    source = Column("source", String)
    url = Column("url", String)
    dropped_at = Column("dropped_at", String)


class LogCrawler(Base):
    __tablename__ = "log_crawler"
    id = Column(Integer, primary_key=True)
    item_status = Column("item_status", String)
    source = Column("source", String)
    url = Column("url", String)
    created_at = Column("created_at", String)
