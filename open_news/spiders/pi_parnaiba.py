from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from open_news.items import NewsItem
from open_news.loaders.pi_parnaiba import CostaNorteNewsLoader, WordpressNewsLoader
from open_news.spiders._base.classic_blogger import ClassicBloggerSpider
from open_news.spiders._base.modern_blogger import ModernBloggerSpider


class PiParnaibaClassicBloggerSpider(ClassicBloggerSpider):
    name = "pi_parnaiba_classic_blogger"
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


class PiParnaibaModernBloggerSpider(ModernBloggerSpider):
    name = "pi_parnaiba_modern_blogger"
    allowed_domains = [
        "portaldoaguia.com.br",
        "portalphb.com.br",
        "portallitoralnoticias.com.br",
        "divulgaphb.com.br",
        "phbnews24horas.com.br",
    ]
    start_urls = [
        "https://www.portaldoaguia.com.br/",
        "https://www.portalphb.com.br/",
        "https://www.portallitoralnoticias.com.br/",
        "https://www.divulgaphb.com.br/",
        "https://www.phbnews24horas.com.br/",
    ]


class BlogDoSilvaSpider(Spider):
    today = date.today()
    name = "pi_parnaiba_blog_do_silva"

    allowed_domains = ["blogdobsilva.com.br"]
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


class CostaNorteSpider(Spider):
    today = date.today()
    name = "pi_parnaiba_costa_norte"

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
