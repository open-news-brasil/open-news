from itemadapter import ItemAdapter
from open_news.items import NewsItem
from open_news.pipelines import BaseNewsPipeline


class HashCalculatorPipeline(BaseNewsPipeline):

    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        adapter['hash'] = hash(
            adapter.get('posted_at') +
            adapter.get('title') +
            adapter.get('link') +
            ' '.join(adapter.get('content', []))
        )
        return adapter.item
