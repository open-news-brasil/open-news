from datetime import date, datetime

from scrapy.http.response.html import HtmlResponse

from open_news.loaders import NewsLoader
from open_news.items import NewsItem
from open_news.spiders._base import BaseSpider


class SimplePageSpider(BaseSpider):
    today = date.today()
    loader_class = NewsLoader
    post_selector = ".post.hentry"

    def parse(self, response: HtmlResponse):
        for post in response.css(self.post_selector):
            news = self.loader_class(NewsItem(), post)

            for attribute, selectors in self.get_selectors():
                for selector in selectors:
                    news.add_xpath(attribute, selector)

            posted_at = news.get_output_value("posted_at")
            if datetime.fromisoformat(posted_at).date() != self.today:
                continue

            yield news.load_item()
