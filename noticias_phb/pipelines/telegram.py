from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from os import getenv
from urllib.parse import urlparse, quote_plus

from emoji import emojize
from itemadapter import ItemAdapter
from pyrogram import Client, utils
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from yt_dlp import YoutubeDL
from noticias_phb.items import NewsItem
from noticias_phb.pipelines import BaseNewsPipeline


# Fixes PEER_ID_INVALID for channels
# https://github.com/pyrogram/pyrogram/issues/1314#issuecomment-2187830732
def get_peer_type_fixed(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"


class SendToTelegramPipeline(BaseNewsPipeline):
    max_content_size = 790
    emoji = emojize(':newspaper:')
    chat_id = int(getenv('TELEGRAM_CHAT_ID', '0'))
    telegram = Client(
        name='noticias_phb_bot',
        api_id=getenv('TELEGRAM_API_ID', ''),
        api_hash=getenv('TELEGRAM_API_HASH', ''),
        bot_token=getenv('TELEGRAM_BOT_TOKEN', ''),

    )

    def lines(self, lines_list: list[str]) -> str:
        return '\n\n'.join(lines_list)
    
    def message_title(self, adapter: ItemAdapter) -> str:
        title = adapter.get('title', '').strip()
        return f'{self.emoji} **{title}**'

    def message_content(self, adapter: ItemAdapter) -> str:
        content = ' '.join(adapter.get('content'))
        if len(content) > self.max_content_size:
            content = f'{content[:self.max_content_size]} **[...]**'
        return content

    def message_text(self, adapter: ItemAdapter) -> str:
        link = adapter.get('link')
        domain = urlparse(link).netloc
        content = self.message_content(adapter)

        if content.replace('\n', '') == '':
            return self.lines([
                f'__[{domain}]({link})__',
                self.message_title(adapter)
            ])
        
        return self.lines([
                f'__[{domain}]({link})__',
                self.message_title(adapter),
                content,
            ])
    
    def whatsapp_link(self, adapter: ItemAdapter) -> str:
        message = self.lines([
            self.message_title(adapter).replace('**', '*'),
            f'*Fonte:* {adapter.get('link')}',
            self.message_content(adapter).replace('**', '*'),
            f'{emojize(':mobile_phone:')} Esta e outra notícias, você pode '
            'receber no seu Telegram! Entre agora no canal t.me/noticias_phb'
        ])
        return f'https://api.whatsapp.com/send?text={quote_plus(message)}'
    
    def buttons(self, adapter: ItemAdapter):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Acessar publicação",
                    url=adapter.get('link')
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Compartilhar no Whatsapp",
                    url=self.whatsapp_link(adapter)
                )
            ]
        ])

    async def send_images(self, adapter: ItemAdapter, message: str):
        images = adapter.get('images')

        try:
            if len(images) > 1:
                await self.telegram.send_media_group(
                    chat_id=self.chat_id,
                    media=[
                        InputMediaPhoto(img)
                        for img in images[1:]
                    ]
                )

        finally:
            await self.telegram.send_photo(
                chat_id=self.chat_id,
                photo=images[0],
                caption=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.buttons(adapter)
            )
    
    async def send_video(self, adapter: ItemAdapter, message: str):
        tempdir = TemporaryDirectory()

        try:
            filepath = f'{tempdir.name}/%(id)s.%(ext)s'
            options = {
                'format': 'best[height<=360]',
                'outtmpl': filepath
            }
            with YoutubeDL(options) as ytdl:
                ytdl.download(adapter.get('video'))
            
            for file in Path(tempdir.name).iterdir():
                await self.telegram.send_video(
                    chat_id=self.chat_id,
                    video=str(file),
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.buttons(adapter)
                )

        except Exception:
            await self.telegram.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.buttons(adapter)
            )
        
        finally:
            tempdir.cleanup()

    async def process_item(self, item: NewsItem, spider) -> NewsItem:        
        adapter = ItemAdapter(item)
        message_text = self.message_text(adapter)
        utils.get_peer_type = get_peer_type_fixed
        
        try:
            if not self.telegram.is_connected:
                await self.telegram.start()

            if adapter.get('images'):
                await self.send_images(adapter, message_text)

            elif adapter.get('video'):
                await self.send_video(adapter, message_text)
            
            else:
                await self.telegram.send_message(
                    chat_id=self.chat_id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.buttons(adapter)
                )
        
        except FloodWait as exc:
            print(f'FloodWait - Waiting {exc.value} seconds!')
            sleep(exc.value) # Blocking wait to avoid flood exception
            return await self.process_item(item, spider)
        
        except Exception as exc:
            self.logger.critical('Error trying to send message!', exc_info=True)
            raise exc
        
        else:
            if self.telegram.is_connected:
                await self.telegram.stop()
            return item
