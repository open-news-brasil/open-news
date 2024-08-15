from datetime import date, datetime

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import PostItem


class ClassicBloggerSpider(Spider):
    today = date.today()
    name = "classic_blogger"
    
    allowed_domains = [
        "carlsonpessoa.blogspot.com",
        "portaldocatita.blogspot.com",
        "jornaldaparnaiba.com",
        "phbemnota.com",
        "clickparnaiba.blogspot.com",
        "plantaoparnaiba24horas.com.br"
    ]
    start_urls = [
        "https://carlsonpessoa.blogspot.com/",
        "https://portaldocatita.blogspot.com/",
        "https://www.jornaldaparnaiba.com/",
        "https://www.phbemnota.com/",
        "https://clickparnaiba.blogspot.com/",
        "https://www.plantaoparnaiba24horas.com.br/"
    ]


    def parse(self, response: HtmlResponse):
        for post in response.css('.post.hentry'):
            item = PostItem()

            title, *_ = post.xpath('./h3[@class="post-title entry-title"]/a')
            item['title'] = title.root.text
            item['link'] = title.attrib['href']
            
            content, *_ = post.xpath('./div[@class="post-body entry-content"]')
            item['content'] = content.root.text_content()

            image, *_ = content.xpath('.//img')
            item['image'] = image.attrib['src']

            posted_at, *_ = post.xpath('.//abbr[@class="published"]')
            item['posted_at'] = posted_at.attrib['title']

            if datetime.fromisoformat(item['posted_at']).date() != self.today:
                continue

            yield item
