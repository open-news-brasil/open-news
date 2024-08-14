from datetime import date
from pathlib import Path
from os import getenv
from urllib.parse import urlparse

from pysondb import PysonDB
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from pyrogram import Client
from pyrogram.enums import ParseMode
from noticias_phb.items import PostItem
from noticias_phb.spiders.blogger import BloggerSpider
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


class DuplicatedItemsPipeline(JsonPipeline):

    def process_item(self, item: PostItem, spider: BloggerSpider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() in self.current_scrapped:
            raise DropItem(item)
        return item


class SendToTelegramPipeline(JsonPipeline):
    chat_id = int(getenv('TELEGRAM_CHAT_ID_DEV', '0'))
    max_content_size = 1000
    telegram = Client(
        name='noticias_phb_bot',
        api_id=getenv('TELEGRAM_API_ID', ''),
        api_hash=getenv('TELEGRAM_API_HASH', ''),
        bot_token=getenv('TELEGRAM_BOT_TOKEN', '')
    )

    def lines(self, lines_list: list[str]) -> str:
        return '\n\n'.join(lines_list)

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
    
    async def process_item(self, item: PostItem, spider: BloggerSpider) -> PostItem:
        adapter = ItemAdapter(item)
        if not self.telegram.is_connected:
            await self.telegram.connect()
        await self.telegram.send_photo(
            chat_id=self.chat_id,
            photo=adapter.get('image'),
            caption=self.caption(adapter),
            parse_mode=ParseMode.MARKDOWN
        )
        return item


class AppendItemsPipeline(JsonPipeline):
    
    def process_item(self, item: PostItem, spider: BloggerSpider) -> PostItem:
        adapter = ItemAdapter(item)
        if adapter.asdict() not in self.current_scrapped:
            self.db.add(adapter.asdict())
        return item
