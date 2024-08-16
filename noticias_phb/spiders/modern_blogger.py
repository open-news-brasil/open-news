from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import NewsItem, NewsLoader


class ModernBloggerSpider(Spider):
    today = date.today()
    name = "modern_blogger"

    allowed_domains = [
        "portaldoaguia.com.br",
        "portalphb.com.br",
        "portallitoralnoticias.com.br",
    ]
    start_urls = [
        "https://www.portaldoaguia.com.br/",
        "https://www.portalphb.com.br/",
        "https://www.portallitoralnoticias.com.br/",
    ]

    def parse_post(self, response: HtmlResponse):
        post = response.css(".hentry")[0]
        news = NewsLoader(NewsItem(), post)

        news.add_value("link", response.url)
        news.add_xpath("title", './/h1[contains(@class, "post-title")]/text()')
        news.add_xpath("content", './/div[contains(@class, "post-body")]//*/text()')
        news.add_xpath("images", ".//img/@src")
        news.add_xpath("video", './/iframe[contains(@src, "youtube")]/@src')
        news.add_xpath("posted_at", './/abbr[@class="published"]/@title')
        news.add_xpath("posted_at", './/*[contains(@class, "published")]/@datetime')

        posted_at = news.get_output_value("posted_at")
        if datetime.fromisoformat(posted_at).date() == self.today:
            yield news.load_item()

    def parse(self, response: HtmlResponse):
        for post in response.css(".hentry"):
            link = post.xpath(
                './/h2[contains(@class, "post-title")]//a/@href'
            ).extract_first()
            yield response.follow(link, self.parse_post)
