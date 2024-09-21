from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from open_news.loaders import NewsLoader
from open_news.items import NewsItem


class DualPageSpider(Spider):
    today = date.today()
    loader_class = NewsLoader
    
    news_link_selector = './/h2//a/@href'
    post_selector = '.hentry'

    selectors: dict[str, list[str]] = {
        "title": [],
        "content": [],
        "posted_at": [],
        "video": [],
        "images": [],
    }

    def parse_post(self, response: HtmlResponse):
        post = response.css(self.post_selector)[0]
        news = self.loader_class(NewsItem(), post)

        news.add_value("link", response.url)

        for attribute, selectors in self.selectors.items():
            for selector in selectors:
                news.add_xpath(attribute, selector)

        posted_at = news.get_output_value("posted_at")
        if datetime.fromisoformat(posted_at).date() == self.today:
            yield news.load_item()

    def parse(self, response: HtmlResponse):
        for post in response.css(self.post_selector):
            if link := post.xpath(self.news_link_selector).extract_first():
                yield response.follow(link, self.parse_post)
