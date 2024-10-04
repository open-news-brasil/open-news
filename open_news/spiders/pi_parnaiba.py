from open_news.loaders.pi_parnaiba import CostaNorteNewsLoader, WordpressNewsLoader
from open_news.spiders._base.dual_page import DualPageSpider
from open_news.spiders._base.simple_page import SimplePageSpider
from open_news.spiders._base.blogger import (
    SimplePageBloggerSpider,
    DualPageBloggerSpider,
)


class PiParnaibaSimplePageBloggerSpider(SimplePageBloggerSpider):
    name = "pi_parnaiba_simple_page_blogger"
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


class PiParnaibaDualPageBloggerSpider(DualPageBloggerSpider):
    name = "pi_parnaiba_dual_page_blogger"
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


class PiParnaibaBlogDoSilvaSpider(SimplePageSpider):
    loader_class = WordpressNewsLoader
    name = "pi_parnaiba_blog_do_silva"

    allowed_domains = ["blogdobsilva.com.br"]
    start_urls = ["https://blogdobsilva.com.br/"]

    post_selector = "article.post"
    selectors = {
        "title": ['.//h2[contains(@class, "title")]//a/text()'],
        "link": ['.//h2[contains(@class, "title")]//a/@href'],
        "external_videos": ['.//iframe[contains(@src, "if-cdn.com")]/@src'],
        "content": ['.//div[contains(@class, "content")]//*/text()'],
        "posted_at": ['.//time[contains(@class, "published")]/@datetime'],
    }


class PiParnaibaCostaNorteSpider(DualPageSpider):
    loader_class = CostaNorteNewsLoader
    name = "pi_parnaiba_costa_norte"

    allowed_domains = ["portalcostanorte.com"]
    start_urls = ["https://portalcostanorte.com/"]

    news_link_selector = ".//a[./h2]/@href"
    selectors = {
        "title": ['.//a[contains(@class, "post-title")]/h1/text()'],
        "posted_at": ['.//a[@class="post-date"]/b/text()'],
        "content": [
            './/div[contains(@class, "post-content")]//p/text()',
            './/div[contains(@class, "post-content")]//p/span/text()',
        ],
        "images": [
            './/div[contains(@class, "post-type-content")]//img/@src',
            './/div[contains(@class, "post-content")]//img/@src',
        ],
    }


class PiParnaibaTribunaDeParnaibaSpider(DualPageSpider):
    loader_class = WordpressNewsLoader
    name = "pi_parnaiba_tribuna_de_parnaiba"

    allowed_domains = ["tribunadeparnaiba.com"]
    start_urls = ["https://www.tribunadeparnaiba.com/"]

    news_link_selector = ".//h2//a/@href"
    selectors = {
        "title": ['.//h1[contains(@class, "entry-title")]/text()'],
        "posted_at": ['.//time[contains(@class, "published")]/@datetime'],
        "content": [
            './/div[contains(@class, "entry-content")]//p/text()',
            './/div[contains(@class, "entry-content")]//p/strong/text()',
            './/div[contains(@class, "entry-content")]//p/span/text()',
        ],
        "images": [
            './/img[contains(@class, "wp-post-image")]/@src',
            './/img[contains(@class, "wp-image")]/@src',
        ],
    }
