from datetime import timedelta
from os import getenv
from pathlib import Path


BOT_NAME = "open-news"
CHANNEL_LINK = "t.me/s/noticias_phb"
DEBUG = bool(getenv("DEBUG"))

SPIDER_MODULES = ["open_news.spiders"]
NEWSPIDER_MODULE = "open_news.spiders"

PROJECT_ROOT = Path(__file__).parent.parent
MODULE_ROOT = PROJECT_ROOT / BOT_NAME

LOG_FILE = "open_news.log"
LOG_LEVEL = "DEBUG" if DEBUG else "ERROR"
LOG_FILE_APPEND = True

OUTPUT_PATH = PROJECT_ROOT / "data"
OUTPUT_FILE = OUTPUT_PATH / "news.json"
OUTPUT_MAX_DAYS_PERSISTENCE = timedelta(6)

CLOSESPIDER_TIMEOUT = 4 * 60
CONCURRENT_ITEMS = 10
CONCURRENT_REQUESTS = 10

USER_AGENT = f"Notícias de Parnaíba ({CHANNEL_LINK})"
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
    "open_news.pipelines.items_to_ignore.ItemsToIgnorePipeline": 100,
    "open_news.pipelines.deduplication.DeduplicationPipeline": 200,
    "open_news.pipelines.telegram.TelegramPipeline": None
    if TELEGRAM_PIPELINE_DISABLED
    else 300,
    "open_news.pipelines.save.SavePipeline": 400,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
