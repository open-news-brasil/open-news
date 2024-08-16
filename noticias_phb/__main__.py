from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from noticias_phb.spiders import modern_blogger, classic_blogger, wordpress


spiders = [
    classic_blogger.ClassicBloggerSpider,
    modern_blogger.ModernBloggerSpider,
    wordpress.WordpressSpider,
]

if __name__ == "__main__":
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    for spider in spiders:
        process.crawl(spider)
    process.start()
