from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from noticias_phb.items import PostItem


class BloggerSpider(Spider):

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

            yield item


class BlogDoPessoaSpider(BloggerSpider):
    name = "blog_do_pessoa"
    allowed_domains = ["carlsonpessoa.blogspot.com"]
    start_urls = ["https://carlsonpessoa.blogspot.com/"]


class PortalDoCatitaSpider(BloggerSpider):
    name = "portal_do_catita"
    allowed_domains = ["portaldocatita.blogspot.com"]
    start_urls = ["https://portaldocatita.blogspot.com/"]


class JornalDaParnaibaSpider(BloggerSpider):
    name = "jornal_da_parnaiba"
    allowed_domains = ["www.jornaldaparnaiba.com"]
    start_urls = ["https://www.jornaldaparnaiba.com/"]


class PhbEmNotaSpider(BloggerSpider):
    name = "phb_em_nota"
    allowed_domains = ["www.phbemnota.com"]
    start_urls = ["https://www.phbemnota.com/"]


class ClickParnaibaSpider(BloggerSpider):
    name = "click_parnaiba"
    allowed_domains = ["clickparnaiba.blogspot.com"]
    start_urls = ["https://clickparnaiba.blogspot.com/"]
