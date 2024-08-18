from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from noticias_phb.items import NewsItem
from noticias_phb.pipelines import BaseNewsPipeline


class DeduplicationPipeline(BaseNewsPipeline):
    allowed_similarity = 0.8
    items: list[ItemAdapter] = []

    def get_text_similatiry(self, text1: str, text2: str) -> float:
        try:
            vectorizer = CountVectorizer()
            vectors = vectorizer.fit_transform([text1, text2])
            dense_vectors = vectors.toarray()
            similarity = cosine_similarity(dense_vectors[0:1], dense_vectors[1:2])[0][0]
            return similarity
        
        except ValueError:
            return 0
    
    def is_similar(self, text1: str, text2: str) -> bool:
        return self.get_text_similatiry(text1.lower(), text2.lower()) >= self.allowed_similarity

    def has_equivalent_item(self, adapter: ItemAdapter) -> bool:
        link = adapter.get("link")
        title = adapter.get("title")
        content = " ".join(adapter.get("content"))

        for scrapped in self.current_scrapped:
            if self.is_similar(link, scrapped['link']):
                return True
            elif self.is_similar(title, scrapped['title']):
                return True
            elif self.is_similar(content, ' '.join(scrapped['content'])):
                return True
            
        for item in self.items:
            if self.is_similar(link, item.get('link', '')):
                return True
            elif self.is_similar(title, item.get('title', '')):
                return True
            elif self.is_similar(content, ' '.join(item.get('content', []))):
                return True
            
        return False

    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        if self.has_equivalent_item(adapter):
            raise DropItem(item)
        self.items.append(adapter)
        return item
