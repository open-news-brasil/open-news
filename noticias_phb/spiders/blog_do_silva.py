from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import NewsItem, NewsLoader


class WordpressNewsLoader(NewsLoader):
    @staticmethod
    def content_in(values: list[str] | None):
        for line in NewsLoader.content_in(values):
            if "compartilhe isso:" in line.lower():
                break
            yield line


class BlogDoSilvaSpider(Spider):
    today = date.today()
    name = "blog_do_silva"

    allowed_domains = [
        "blogdobsilva.com.br",
    ]
    start_urls = ["https://blogdobsilva.com.br/"]

    def parse(self, response: HtmlResponse):
        for post in response.xpath('//article[contains(@id, "post")]'):
            news = WordpressNewsLoader(NewsItem(), post)

            news.add_xpath("title", './/h2[contains(@class, "title")]//a/text()')
            news.add_xpath("link", './/h2[contains(@class, "title")]//a/@href')
            news.add_xpath("content", './/div[contains(@class, "content")]//*/text()')
            news.add_xpath("images", ".//img/@src")
            news.add_xpath("video", './/iframe[contains(@src, "youtube")]/@src')
            news.add_xpath(
                "posted_at", './/time[contains(@class, "published")]/@datetime'
            )

            posted_at = news.get_output_value("posted_at")
            if datetime.fromisoformat(posted_at).date() != self.today:
                continue

            yield news.load_item()
