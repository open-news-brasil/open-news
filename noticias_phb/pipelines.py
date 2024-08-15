import asyncio

from datetime import date
from pathlib import Path
from os import getenv
from urllib.parse import urlparse

from pysondb import PysonDB
from thefuzz.fuzz import partial_ratio
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from pyrogram import Client, utils
from pyrogram.enums import ParseMode
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

    def has_equivalent_title(self, title: str) -> bool:
        for scrapped in self.current_scrapped_titles:
            if partial_ratio(title.lower(), scrapped) >= 80:
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

    def caption(self, item: ItemAdapter) -> str:
        title = item.get('title', '').strip()
        link = item.get('link')
        domain = urlparse(link).netloc
        content = item.get('content', '').strip().strip('\n')

        if len(content) > self.max_content_size:
            content = f'{content[:self.max_content_size]}...'

        if content.replace('\n', '') == '':
            return self.lines([
                f'**{title}**',
                f'**Fonte:** __[{domain}]({link})__'
            ])
        
        return self.lines([
                f'**{title}**',
                content,
                f'**Fonte:** __[{domain}]({link})__'
            ])
    
    async def process_item(self, item: PostItem, spider) -> PostItem:
        adapter = ItemAdapter(item)
        if not self.telegram.is_connected:
            utils.get_peer_type = self.get_peer_type_new
            await self.telegram.connect()
        await self.telegram.send_photo(
            chat_id=self.chat_id,
            photo=adapter.get('image'),
            caption=self.caption(adapter),
            parse_mode=ParseMode.MARKDOWN
        )
        await asyncio.sleep(30)
        return item


class AppendItemsPipeline(JsonPipeline):
    
    def process_item(self, item: PostItem, spider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() not in self.current_scrapped:
            self.db.add(adapter.asdict())
        return item
