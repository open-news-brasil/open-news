from abc import ABC
from datetime import date
from logging import getLogger

from pysondb import PysonDB
from noticias_phb.settings import OUTPUT_PATH, DATE_FORMAT, PROJECT_ROOT


class BaseNewsPipeline(ABC):
    logger = getLogger("pipeline")
    today = date.today().strftime(DATE_FORMAT)
    data_folder_path = PROJECT_ROOT / f"{OUTPUT_PATH}"
    data_path = data_folder_path / "news.json"

    @property
    def db(self) -> PysonDB:
        self.data_folder_path.mkdir(exist_ok=True)
        return PysonDB(str(self.data_path))

    @property
    def current_scrapped(self) -> list[dict]:
        return list(self.db.get_all().values())

    @property
    def current_scrapped_links(self) -> list[str]:
        return [link for value in self.current_scrapped if (link := value.get("link"))]

    @property
    def current_scrapped_titles(self) -> list[str]:
        return [
            title.lower()
            for value in self.current_scrapped
            if (title := value.get("title"))
        ]
