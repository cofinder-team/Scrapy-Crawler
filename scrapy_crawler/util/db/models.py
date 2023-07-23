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
    type = Column("type", Boolean, primary_key=True)
