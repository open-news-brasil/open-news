from abc import ABC
from datetime import date
from pathlib import Path

from pysondb import PysonDB
from noticias_phb.settings import OUTPUT_PATH, DATE_FORMAT


class BasePipeline(ABC):
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
    
    @property
    def current_scrapped_links(self) -> list[str]:
        return [
            link
            for value in self.current_scrapped
            if (link := value.get('link'))
        ]
    
    @property
    def current_scrapped_titles(self) -> list[str]:
        return [
            title.lower()
            for value in self.current_scrapped
            if (title := value.get('title'))
        ]
