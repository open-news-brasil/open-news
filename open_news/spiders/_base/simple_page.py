from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from open_news.loaders import NewsLoader
from open_news.items import NewsItem


class SimplePageSpider(Spider):
    today = date.today()
    loader_class = NewsLoader

    post_selector = ".post.hentry"

    selectors: dict[str, list[str]] = {
        "title": [],
        "link": [],
        "content": [],
        "posted_at": [],
        "video": [],
        "images": [],
    }

    def parse(self, response: HtmlResponse):
        for post in response.css(self.post_selector):
            news = self.loader_class(NewsItem(), post)

            for attribute, selectors in self.selectors.items():
                for selector in selectors:
                    news.add_xpath(attribute, selector)

            posted_at = news.get_output_value("posted_at")
            if datetime.fromisoformat(posted_at).date() != self.today:
                continue

            yield news.load_item()
