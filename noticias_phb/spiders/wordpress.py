from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import PostItem


class WordpressSpider(Spider):
    today = date.today()
    name = "wordpress"
    
    allowed_domains = [
        "blogdobsilva.com.br",
    ]
    start_urls = [
        "https://blogdobsilva.com.br/"
    ]


    def parse(self, response: HtmlResponse):
        for post in response.xpath('//article[contains(@id, "post")]'):
            item = PostItem()

            title, *_ = post.xpath('.//h2[contains(@class, "title")]/a')
            item['title'] = title.root.text
            item['link'] = title.attrib['href']
            
            content, *_ = post.xpath('.//div[contains(@class, "content")]')
            item['content'] = content.root.text_content()

            try:
                image, *_ = content.xpath('.//img')
                item['image'] = image.attrib['src']
            
            except ValueError:
                item['image'] = None

            posted_at, *_ = post.xpath('.//time[contains(@class, "published")]')
            item['posted_at'] = posted_at.attrib['datetime']

            if datetime.fromisoformat(item['posted_at']).date() != self.today:
                continue

            yield item
