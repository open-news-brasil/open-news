import uvloop

from logging import getLogger
from pyrogram.client import Client
from noticias_phb.settings import TELEGRAM_OPTIONS


telegram = Client(**TELEGRAM_OPTIONS)
logger = getLogger(__name__)


@telegram.on_message()
async def hello(client, message):
    logger.info(f"{message.chat.id} = {message.text}")


if __name__ == "__main__":
    uvloop.install()
    telegram.run()
