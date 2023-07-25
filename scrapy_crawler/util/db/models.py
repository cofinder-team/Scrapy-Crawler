from typing import Any

from sqlalchemy import Boolean, Column, ForeignKey, Integer, LargeBinary, String
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
    last_crawled = Column("last_crawled", String)
    writer = Column("writer", String)
    title = Column("title", String)
    content = Column("content", String)
    apple_care = Column("apple_care", Boolean)


class ItemIpad(Base):
    __tablename__ = "item_ipad"
    id = Column(Integer, primary_key=True)
    type = Column("type", ForeignKey("item.type"))
    model = Column("model", ForeignKey("model.type"))
    option = Column("option", Integer)
    generation = Column("gen", Integer)
    ssd = Column("storage", Integer)
    cellular = Column("cellular", Boolean)
