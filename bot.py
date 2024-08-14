import uvloop

from os import getenv
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.filters import channel

uvloop.install()

app = Client(
    name='noticias_phb_bot',
    api_id=getenv('TELEGRAM_API_ID', ''),
    api_hash=getenv('TELEGRAM_API_HASH', ''),
    bot_token=getenv('TELEGRAM_BOT_TOKEN', '')
)

@app.on_message(channel)
async def start(client: Client, message: Message):
    pass
    

if __name__ == '__main__':
    app.run()
