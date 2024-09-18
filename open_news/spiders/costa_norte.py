from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from open_news.items import NewsItem, NewsLoader


class CostaNorteNewsLoader(NewsLoader):
    @staticmethod
    def posted_at_in(values: list[str] | None):
        if values is None:
            return []
        for value in values:
            dt_object = datetime.strptime(value, "%d/%m/%Y")
            yield str(dt_object.isoformat())


class CostaNorteSpider(Spider):
    today = date.today()
    name = "costa_norte"

    allowed_domains = ["portalcostanorte.com"]
    start_urls = ["https://portalcostanorte.com/"]

    def parse_post(self, response: HtmlResponse):
        post = response.css(".hentry")[0]
        news = CostaNorteNewsLoader(NewsItem(), post)

        news.add_value("link", response.url)
        news.add_xpath("title", './/a[contains(@class, "post-title")]/h1/text()')
        news.add_xpath("content", './/div[contains(@class, "post-content")]//p/text()')
        news.add_xpath(
            "content", './/div[contains(@class, "post-content")]//p/span/text()'
        )
        news.add_xpath(
            "images", './/div[contains(@class, "post-type-content")]//img/@src'
        )
        news.add_xpath("images", './/div[contains(@class, "post-content")]//img/@src')
        news.add_xpath("video", './/iframe[contains(@src, "youtube")]/@src')
        news.add_xpath("posted_at", './/a[@class="post-date"]/b/text()')

        posted_at = news.get_output_value("posted_at")
        if datetime.fromisoformat(posted_at).date() == self.today:
            yield news.load_item()

    def parse(self, response: HtmlResponse):
        for post in response.css(".hentry"):
            if link := post.xpath(".//a[./h2]/@href").extract_first():
                yield response.follow(link, self.parse_post)
