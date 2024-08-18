from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import NewsLoader, NewsItem


class ClassicBloggerSpider(Spider):
    today = date.today()
    name = "classic_blogger"

    allowed_domains = [
        "carlsonpessoa.blogspot.com",
        "portaldocatita.blogspot.com",
        "clickparnaiba.blogspot.com",
        "jornaldaparnaiba.com",
        "phbemnota.com",
        "plantaoparnaiba24horas.com.br",
    ]
    start_urls = [
        "https://carlsonpessoa.blogspot.com/",
        "https://portaldocatita.blogspot.com/",
        "https://clickparnaiba.blogspot.com/",
        "https://www.jornaldaparnaiba.com/",
        "https://www.phbemnota.com/",
        "https://www.plantaoparnaiba24horas.com.br/",
    ]

    def parse(self, response: HtmlResponse):
        for post in response.css(".post.hentry"):
            news = NewsLoader(NewsItem(), post)
            news.add_xpath("title", './h3[@class="post-title entry-title"]/a/text()')
            news.add_xpath("link", './h3[@class="post-title entry-title"]/a/@href')
            news.add_xpath(
                "content", './div[@class="post-body entry-content"]//*/text()'
            )
            news.add_xpath("images", ".//img/@src")
            news.add_xpath("video", './/iframe[contains(@src, "youtube")]/@src')
            news.add_xpath("posted_at", './/abbr[@class="published"]/@title')

            posted_at = news.get_output_value("posted_at")
            if datetime.fromisoformat(posted_at).date() != self.today:
                continue

            yield news.load_item()
