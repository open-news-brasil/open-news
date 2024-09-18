from abc import ABC
from datetime import datetime
from logging import getLogger

from pysondb import PysonDB
from open_news.settings import OUTPUT_FILE, OUTPUT_MAX_DAYS_PERSISTENCE, OUTPUT_PATH


class BaseNewsPipeline(ABC):
    logger = getLogger("pipeline")

    @property
    def db(self) -> PysonDB:
        OUTPUT_PATH.mkdir(exist_ok=True)
        return PysonDB(str(OUTPUT_FILE))

    @property
    def current_scrapped(self) -> list[dict]:
        return list(self.db.get_all().values())[::-1]

    def _old_registry(self, registry: dict) -> bool:
        posted_at = datetime.fromisoformat(registry["posted_at"])
        now = datetime.now(posted_at.tzinfo)
        return (now - posted_at) >= OUTPUT_MAX_DAYS_PERSISTENCE

    def open_spider(self, spider):
        db_content = self.db.get_by_query(self._old_registry)
        for item_id in db_content:
            self.db.delete_by_id(item_id)
