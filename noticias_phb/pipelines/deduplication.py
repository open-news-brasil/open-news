from thefuzz.fuzz import partial_ratio
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from noticias_phb.classifier.classifier import NewsClassifier
from noticias_phb.items import NewsItem
from noticias_phb.pipelines import BaseNewsPipeline


class DeduplicationPipeline(BaseNewsPipeline):
    items: list[ItemAdapter] = []

    def setup(self):
        self.ALLOWED_SIMILARITY = 0.7

    def has_equivalent_title(self, title: str) -> bool:
        for scrapped in self.current_scrapped_titles:
            if partial_ratio(title.lower(), scrapped) >= 80:
                return True
        for item in self.items:
            if partial_ratio(title.lower(), item.get("title", "").lower()) >= 70:
                return True
        return False

    def has_too_much_similarity(self,content: str):
        for scrapped in self.current_scrapped_content:
            if NewsClassifier.news_content_similarity(content.lower(),scrapped) >= self.ALLOWED_SIMILARITY:
                return True
        for item in self.items:
            if NewsClassifier.news_content_similarity(content.lower(),item.get("title", "").lower()) >= self.ALLOWED_SIMILARITY:
                return True
        return False

    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        link = adapter.get("link")
        title: str = adapter.get("title")
        content: str = "".join(adapter.get("content"))
        if link in self.current_scrapped_links:
            raise DropItem(item)
        elif self.has_equivalent_title(title):
            raise DropItem(item)
        elif self.has_too_much_similarity(content):
            raise DropItem(item)
        self.items.append(adapter)
        return item
