from scrapy import Spider
from scrapy.http.response.html import HtmlResponse


class BloggerSpider(Spider):

    def parse(self, response: HtmlResponse):
        for post in response.css('.post.hentry'):
            title, *_ = post.xpath('./h3[@class="post-title entry-title"]/a')
            content, *_ = post.xpath('./div[@class="post-body entry-content"]')
            image, *_ = content.xpath('.//img')
            yield {
                "title": title.root.text,
                "image": image.attrib['src'],
                "conten": content.root.text_content(),
                "link": title.attrib['href']
            }


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
