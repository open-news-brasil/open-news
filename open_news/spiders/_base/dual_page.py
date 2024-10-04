from datetime import date, datetime

from scrapy.http.response.html import HtmlResponse

from open_news.loaders import NewsLoader
from open_news.items import NewsItem
from open_news.spiders._base import BaseSpider


class DualPageSpider(BaseSpider):
    today = date.today()
    loader_class = NewsLoader
    news_link_selector = ".//h2//a/@href"
    post_selector = ".hentry"

    def parse_post(self, response: HtmlResponse):
        post = response.css(self.post_selector)[0]
        news = self.loader_class(NewsItem(), post)

        news.add_value("link", response.url)

        for attribute, selectors in self.get_selectors():
            for selector in selectors:
                news.add_xpath(attribute, selector)

        posted_at = news.get_output_value("posted_at")
        if datetime.fromisoformat(posted_at).date() == self.today:
            yield news.load_item()

    def parse(self, response: HtmlResponse):
        for post in response.css(self.post_selector):
            if link := post.xpath(self.news_link_selector).extract_first():
                yield response.follow(link, self.parse_post)
