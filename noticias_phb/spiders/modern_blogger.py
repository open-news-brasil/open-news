from contextlib import suppress
from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import PostItem


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
        post = response.css('.hentry')
        item = PostItem()
        
        with suppress(ValueError):
            title, *_ = post.xpath('.//h1[contains(@class, "post-title"]')
            item['title'] = title.root.text
            item['link'] = response.url
            
            content, *_ = post.xpath('.//div[contains(@class, "post-body")]')
            item['content'] = content.root.text_content()

            image, *_ = content.xpath('.//img')
            item['image'] = image.attrib['src']

            posted_at, *_ = post.xpath('.//abbr[@class="published"]')
            item['posted_at'] = posted_at.attrib['title']

            if datetime.fromisoformat(item['posted_at']).date() == self.today:
                yield item


    def parse(self, response: HtmlResponse):
        for post in response.css('.hentry'):
            link, *_ = post.xpath('.//h2[contains(@class, "post-title")]/a')
            yield response.follow(link, self.parse_post)
