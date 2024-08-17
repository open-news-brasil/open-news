from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
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
from noticias_phb.settings import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_MAX_CONTENT_SIZE,
    TELEGRAM_OPTIONS,
)


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
    emoji = emojize(":newspaper:")

    def lines(self, lines_list: list[str]) -> str:
        return "\n\n".join(lines_list)

    def message_title(self, adapter: ItemAdapter) -> str:
        title = adapter.get("title", "").strip()
        return f"{self.emoji} **{title}**"

    def message_content(self, adapter: ItemAdapter) -> str:
        content = " ".join(adapter.get("content"))
        if len(content) > TELEGRAM_MAX_CONTENT_SIZE:
            content = content[:TELEGRAM_MAX_CONTENT_SIZE] + " **[...]**"
        return content

    def message_text(self, adapter: ItemAdapter) -> str:
        link = adapter.get("link")
        domain = urlparse(link).netloc
        content = self.message_content(adapter)

        if content.replace("\n", "") == "":
            return self.lines([f"__[{domain}]({link})__", self.message_title(adapter)])

        return self.lines(
            [
                f"__[{domain}]({link})__",
                self.message_title(adapter),
                content,
            ]
        )

    def whatsapp_link(self, adapter: ItemAdapter) -> str:
        message = self.lines(
            [
                self.message_title(adapter).replace("**", "*"),
                "*Fonte:* " + adapter.get("link"),
                self.message_content(adapter).replace("**", "*"),
                emojize(":mobile_phone:") + " Esta e outra notícias, você pode "
                "receber no seu Telegram! Entre agora no canal t.me/noticias_phb",
            ]
        )
        return "https://api.whatsapp.com/send?text=" + quote_plus(message)

    def buttons(self, adapter: ItemAdapter):
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Acessar publicação", url=adapter.get("link")
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Compartilhar no Whatsapp", url=self.whatsapp_link(adapter)
                    )
                ],
            ]
        )

    async def send_images(self, telegram: Client, adapter: ItemAdapter, message: str):
        images = adapter.get("images")

        try:
            if len(images) > 1:
                await telegram.send_media_group(
                    chat_id=TELEGRAM_CHAT_ID,
                    media=[InputMediaPhoto(img) for img in images[1:10]],
                )
        
        except Exception as exc:
            self.logger.error(str(exc), exc_info=True)

        finally:
            await telegram.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=images[0],
                caption=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.buttons(adapter),
            )

    async def send_video(self, telegram: Client, adapter: ItemAdapter, message: str):
        tempdir = TemporaryDirectory()

        try:
            filepath = tempdir.name + "/%(id)s.%(ext)s"
            options = {"format": "best[height<=360]", "outtmpl": filepath}
            with YoutubeDL(options) as ytdl:
                ytdl.download(adapter.get("video"))

            for file in Path(tempdir.name).iterdir():
                await telegram.send_video(
                    chat_id=TELEGRAM_CHAT_ID,
                    video=str(file),
                    caption=message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=self.buttons(adapter),
                )

        except Exception:
            await telegram.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=self.buttons(adapter),
            )

        finally:
            tempdir.cleanup()

    async def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        message_text = self.message_text(adapter)
        utils.get_peer_type = get_peer_type_fixed

        async with Client(**TELEGRAM_OPTIONS) as telegram:
            try:
                if adapter.get("video"):
                    await self.send_video(telegram, adapter, message_text)
                
                elif adapter.get("images"):
                    await self.send_images(telegram, adapter, message_text)

                else:
                    await telegram.send_message(
                        chat_id=TELEGRAM_CHAT_ID,
                        text=message_text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=self.buttons(adapter),
                    )

            except FloodWait as exc:
                self.logger.error(str(exc))
                sleep(exc.value)  # Blocking wait to avoid flood exception
                return await self.process_item(item, spider)

            except Exception as exc:
                self.logger.critical(str(exc), exc_info=True)
                raise exc

            else:
                return item
