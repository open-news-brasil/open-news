import uvloop

from datetime import datetime
from logging import getLogger
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from noticias_phb.spiders import modern_blogger, classic_blogger, wordpress
from noticias_phb.settings import PROJECT_ROOT, BOT_NAME


logger = getLogger(__name__)
lock_file = PROJECT_ROOT / f"{BOT_NAME}.lock"
settings = get_project_settings()
spiders = [
    classic_blogger.ClassicBloggerSpider,
    modern_blogger.ModernBloggerSpider,
    wordpress.WordpressSpider,
]


if __name__ == "__main__":
    if lock_file.exists():
        logger.warning('Skipping because already exists an lock file!')

    else:
        uvloop.install()
        process = CrawlerProcess(settings)
        for spider in spiders:
            process.crawl(spider)
        lock_file.write_text(str(datetime.now()))
        process.start()
        lock_file.unlink(missing_ok=True)
