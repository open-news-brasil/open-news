import time

from datetime import date
from pathlib import Path
from os import getenv
from urllib.parse import urlparse

from pysondb import PysonDB
from emoji import emojize
from thefuzz.fuzz import partial_ratio
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from pyrogram import Client, utils
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from noticias_phb.items import PostItem
from noticias_phb.settings import OUTPUT_PATH, DATE_FORMAT


class JsonPipeline:
    today = date.today().strftime(DATE_FORMAT)
    scrapping_path = Path(__file__).parent.parent / f'{OUTPUT_PATH}'
    today_scrapping_path = scrapping_path / f'{today}.json'

    @property
    def db(self) -> PysonDB:
        self.scrapping_path.mkdir(exist_ok=True)
        return PysonDB(str(self.today_scrapping_path))
    
    @property
    def current_scrapped(self) -> list[dict]:
        return list(self.db.get_all().values())
    
    @property
    def current_scrapped_links(self) -> list[str]:
        return [
            link
            for value in self.current_scrapped
            if (link := value.get('link'))
        ]
    
    @property
    def current_scrapped_titles(self) -> list[str]:
        return [
            title.lower()
            for value in self.current_scrapped
            if (title := value.get('title'))
        ]


class DuplicatedItemsPipeline(JsonPipeline):
    items: list[ItemAdapter] = []

    def has_equivalent_title(self, title: str) -> bool:
        for scrapped in self.current_scrapped_titles:
            if partial_ratio(title.lower(), scrapped) >= 80:
                return True
        for item in self.items:
            if partial_ratio(title.lower(), item.get('title', '').lower()) >= 80:
                return True
        return False

    def process_item(self, item: PostItem, spider) -> PostItem:
        adapter = ItemAdapter(item)
        link = adapter.get('link')
        title = adapter.get('title')
        if link in self.current_scrapped_links:
            raise DropItem(item)
        elif self.has_equivalent_title(title):
            raise DropItem(item)
        self.items.append(item)
        return item


class SendToTelegramPipeline(JsonPipeline):
    chat_id = int(getenv('TELEGRAM_CHAT_ID', '0'))
    max_content_size = 790
    telegram = Client(
        name='noticias_phb_bot',
        api_id=getenv('TELEGRAM_API_ID', ''),
        api_hash=getenv('TELEGRAM_API_HASH', ''),
        bot_token=getenv('TELEGRAM_BOT_TOKEN', '')
    )

    def lines(self, lines_list: list[str]) -> str:
        return '\n\n'.join(lines_list)
    
    @staticmethod
    def get_peer_type_new(peer_id: int) -> str:
        peer_id_str = str(peer_id)
        if not peer_id_str.startswith("-"):
            return "user"
        elif peer_id_str.startswith("-100"):
            return "channel"
        else:
            return "chat"

    def caption(self, adapter: ItemAdapter) -> str:
        title = adapter.get('title', '').strip()
        link = adapter.get('link')
        domain = urlparse(link).netloc
        content = adapter.get('content', '').strip().strip('\n')
        emoji = emojize(':newspaper:')

        if len(content) > self.max_content_size:
            content = f'{content[:self.max_content_size]}[...]'

        if content.replace('\n', '') == '':
            return self.lines([
                f'__[{domain}]({link})__',
                f'{emoji} **{title}**',
            ])
        
        return self.lines([
                f'__[{domain}]({link})__',
                f'{emoji} **{title}**',
                content,
            ])
    
    def buttons(self, adapter: ItemAdapter):
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text="Ler matéria no site",
                url=adapter.get('link')
            )
        ]])
    
    async def process_item(self, item: PostItem, spider) -> PostItem:        
        adapter = ItemAdapter(item)
        message_text = self.caption(adapter)
        utils.get_peer_type = self.get_peer_type_new
        
        try:
            if not self.telegram.is_connected:
                await self.telegram.connect()
                await self.telegram.authorize()

            if image := adapter.get('image'):
                await self.telegram.send_photo(
                    chat_id=self.chat_id,
                    photo=image,
                    caption=message_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.buttons(adapter)
                )
            
            else:
                await self.telegram.send_message(
                    chat_id=self.chat_id,
                    text=message_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.buttons(adapter)
                )
        
        except FloodWait as exc:
            print(f'FloodWait - Waiting {exc.value} seconds!')
            # Blocking wait to avoid flood exception
            time.sleep(exc.value)
            return await self.process_item(item, spider)
        
        finally:
            await self.telegram.disconnect()
            return item


class AppendItemsPipeline(JsonPipeline):
    
    def process_item(self, item: PostItem, spider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() not in self.current_scrapped:
            self.db.add(adapter.asdict())
        return item
