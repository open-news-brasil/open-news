from os import getenv
from pathlib import Path


BOT_NAME = "noticias_phb"

SPIDER_MODULES = ["noticias_phb.spiders"]
NEWSPIDER_MODULE = "noticias_phb.spiders"

OUTPUT_PATH = "data"
DATE_FORMAT = "%Y-%m-%d"
PROJECT_ROOT = Path(__file__).parent.parent
MODULE_ROOT = PROJECT_ROOT / BOT_NAME

LOG_FILE = "noticias_phb.log"
LOG_LEVEL = "ERROR"
LOG_FILE_APPEND = True

CLOSESPIDER_TIMEOUT = 240
CONCURRENT_ITEMS = 1
CONCURRENT_REQUESTS = 1

USER_AGENT = "Notícias de Parnaíba (t.me/noticias_phb)"
ROBOTSTXT_OBEY = True

TELEGRAM_MAX_CONTENT_SIZE = 790
TELEGRAM_PIPELINE_DISABLED = bool(getenv("TELEGRAM_PIPELINE_DISABLED"))
TELEGRAM_API_ID = getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = getenv("TELEGRAM_API_HASH", "")
TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID", "me")
TELEGRAM_BOT_TOKENS = [
    token for i in range(4) if (token := getenv(f"TELEGRAM_BOT_REPLICA_{i}_TOKEN"))
]

ITEM_PIPELINES = {
    "noticias_phb.pipelines.deduplication.DeduplicationPipeline": 100,
    "noticias_phb.pipelines.telegram.TelegramPipeline": None
    if TELEGRAM_PIPELINE_DISABLED
    else 200,
    "noticias_phb.pipelines.save.SavePipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
