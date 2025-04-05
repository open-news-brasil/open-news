from datetime import date
from functools import lru_cache
from typing import ItemsView

from scrapy import Spider
from itemloaders import ItemLoader


class BaseSpider(Spider):
    today: date = date.today()
    loader_class: type[ItemLoader]
    post_css_selector: str

    default_selectors: dict[str, list[str]] = {
        "images": [".//img/@src"],
        "videos": [".//video/@src"],
        "youtube": ['.//iframe[contains(@src, "youtube")]/@src'],
        "instagram": ['.//iframe[contains(@src, "instagram")]/@src'],
    }

    selectors: dict[str, list[str]] = {
        "title": [],
        "link": [],
        "content": [],
        "posted_at": [],
        "videos": [],
        "external_videos": [],
        "images": [],
        "youtube": [],
        "instagram": [],
    }

    @lru_cache
    def get_selectors(self) -> ItemsView[str, list[str]]:
        selectors = self.default_selectors.copy()
        selectors.update(self.selectors)
        return selectors.items()
