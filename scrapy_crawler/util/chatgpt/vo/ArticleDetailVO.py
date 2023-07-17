
class ArticleDetailVO:
    def __init__(self, price: int = -1, content: str = "UNKNOWN", writer: str = "UNKNOWN"):
        self.price: int = price
        self.content: str = content
        self.writer: str = writer


    def __str__(self):
        return f"ArticleDetailVO(price={self.price}, content={self.content}, writer={self.writer})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "price": self.price,
            "content": self.content,
            "writer": self.writer
        }

    @staticmethod
    def from_dict(article_detail: dict):
        try:
            return ArticleDetailVO(price=article_detail["price"], content=article_detail["content"], writer=article_detail["writer"])
        except KeyError:
            return ArticleDetailVO()