from datetime import datetime
from open_news.loaders import NewsLoader


class WordpressNewsLoader(NewsLoader):
    @staticmethod
    def content_in(values: list[str] | None):
        for line in NewsLoader.content_in(values):
            if "compartilhe isso:" in line.lower():
                break
            yield line


class CostaNorteNewsLoader(NewsLoader):
    @staticmethod
    def posted_at_in(values: list[str] | None):
        if values is None:
            return []
        for value in values:
            dt_object = datetime.strptime(value, "%d/%m/%Y")
            yield str(dt_object.isoformat())