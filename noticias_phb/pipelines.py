from datetime import date
from pathlib import Path

from pysondb import PysonDB
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from noticias_phb.items import PostItem
from noticias_phb.spiders.blogger import BloggerSpider
from noticias_phb.settings import OUTPUT_PATH, DATE_FORMAT


class JsonPipeline:
    today = date.today().strftime(DATE_FORMAT)
    scrapping_path = Path(__file__).parent.parent / f'{OUTPUT_PATH}'
    today_scrapping_path = scrapping_path / f'{today}.json'

    @property
    def db(self) -> PysonDB:
        self.scrapping_path.mkdir(exist_ok=True)
        return PysonDB(str(self.today_scrapping_path))
    
    @property
    def current_scrapped(self) -> list[dict]:
        return list(self.db.get_all().values())


class DuplicatedItemsPipeline(JsonPipeline):

    def process_item(self, item: PostItem, spider: BloggerSpider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() in self.current_scrapped:
            raise DropItem(item)
        return item


class SendToTelegramPipeline(JsonPipeline):
    
    def process_item(self, item: PostItem, spider: BloggerSpider) -> PostItem:
        pass


class AppendItemsPipeline(JsonPipeline):
    
    def process_item(self, item: PostItem, spider: BloggerSpider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() not in self.current_scrapped:
            self.db.add(adapter.asdict())
        return item
