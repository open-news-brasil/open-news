from open_news.spiders._base.dual_page import DualPageSpider
from open_news.spiders._base.simple_page import SimplePageSpider


class SimplePageBloggerSpider(SimplePageSpider):
    selectors = {
        "title": ['./h3[@class="post-title entry-title"]/a/text()'],
        "link": ['./h3[@class="post-title entry-title"]/a/@href'],
        "content": ['./div[@class="post-body entry-content"]//*/text()'],
        "images": ['.//img/@src'],
        "video": ['.//iframe[contains(@src, "youtube")]/@src'],
        "posted_at": ['.//abbr[@class="published"]/@title'],
    }


class DualPageBloggerSpider(DualPageSpider):
    selectors = {
        "title": ['.//h1[contains(@class, "post-title")]/text()'],
        "content": ['.//div[contains(@class, "post-body")]//*/text()'],
        "images": ['.//img/@src'],
        "video": ['.//iframe[contains(@src, "youtube")]/@src'],
        "posted_at": ['.//*[contains(@class, "published")]/@datetime'],
    }
