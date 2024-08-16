from itemadapter import ItemAdapter
from noticias_phb.items import PostItem
from noticias_phb.pipelines import BasePipeline


class SaveDataPipeline(BasePipeline):
    
    def process_item(self, item: PostItem, spider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() not in self.current_scrapped:
            self.db.add(adapter.asdict())
        return item
