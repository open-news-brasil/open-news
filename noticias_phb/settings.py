from os import getenv
from pathlib import Path


BOT_NAME = "noticias_phb"

SPIDER_MODULES = ["noticias_phb.spiders"]
NEWSPIDER_MODULE = "noticias_phb.spiders"

OUTPUT_PATH = "data"
DATE_FORMAT = "%Y-%m-%d"
PROJECT_ROOT = Path(__file__).parent.parent

USER_AGENT = "Notícias de Parnaíba (t.me/noticias_phb)"
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    "noticias_phb.pipelines.deduplication.DuplicatedItemsPipeline": 100,
    "noticias_phb.pipelines.telegram.SendToTelegramPipeline": 200,
    "noticias_phb.pipelines.save.SaveDataPipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

TELEGRAM_API_ID = getenv("TELEGRAM_API_ID", "")
TELEGRAM_API_HASH = getenv("TELEGRAM_API_HASH", "")
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = int(getenv("TELEGRAM_CHAT_ID", "0"))
TELEGRAM_MAX_CONTENT_SIZE = 790
TELEGRAM_OPTIONS = {
    "name": "noticias_phb_bot",
    "api_id": TELEGRAM_API_ID,
    "api_hash": TELEGRAM_API_HASH,
    "bot_token": TELEGRAM_BOT_TOKEN,
}
