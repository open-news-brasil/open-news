from itemadapter import ItemAdapter
from noticias_phb.items import NewsItem
from noticias_phb.pipelines import BaseNewsPipeline


class SaveDataPipeline(BaseNewsPipeline):

    def to_dict(self, adapter: ItemAdapter) -> dict:
        item_keys = adapter.item.fields.keys()
        current_keys = adapter.item.keys()
        complete_dict = adapter.asdict()
        for key in item_keys:
            if key not in current_keys:
                complete_dict[key] = None
        return complete_dict
    
    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        item_dict = self.to_dict(adapter)
        if item_dict not in self.current_scrapped:
            self.db.add(item_dict)
        return item
