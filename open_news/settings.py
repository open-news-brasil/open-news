from datetime import timedelta
from os import getenv
from pathlib import Path


BOT_NAME = "open-news"
DEBUG = bool(getenv("DEBUG"))

TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID", "noticias_phb")
TELEGRAM_QUEUE_URL = getenv("TELEGRAM_QUEUE_URL")
TELEGRAM_QUEUE_REGION = getenv("TELEGRAM_QUEUE_REGION", "us-east-1")
TELEGRAM_PIPELINE_DISABLED = bool(getenv("TELEGRAM_PIPELINE_DISABLED"))

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

USER_AGENT = f"Notícias de Parnaíba (t.me/{TELEGRAM_CHAT_ID})"
ROBOTSTXT_OBEY = True

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
