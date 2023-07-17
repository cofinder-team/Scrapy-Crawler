from vo.ArticleDetailVO import ArticleDetailVO


class ArticleInfoVO:
    def __init__(self, title: str = "UNKNOWN", url: str = "UNKNOWN", date: str = "UNKNOWN", tag: str = "UNKNOWN",
                 level: str = "UNKNOWN"):
        self.title: str = title
        self.url: str = url
        self.date: str = date
        self.tag: str = tag
        self.level: str = level
        self.detail: ArticleDetailVO or None = None

    def add_detail(self, detail: ArticleDetailVO):
        self.detail = detail

    def __str__(self):
        return f"ArticleInfoVO(title={self.title}, url={self.url}, date={self.date}, tag={self.tag}, level={self.level}, detail={self.detail})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        info_dict = {
            "title": self.title,
            "url": self.url,
            "date": self.date,
            "tag": self.tag,
            "level": self.level,
        }

        if self.detail is not None:
            info_dict.update(self.detail.to_dict())

        return info_dict

