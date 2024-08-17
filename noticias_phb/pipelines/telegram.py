from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from urllib.parse import urlparse, quote_plus

from emoji import emojize
from itemadapter import ItemAdapter
from telethon import TelegramClient, Button
from telethon.sessions import MemorySession
from telethon.errors import RPCError, FloodWaitError
from yt_dlp import YoutubeDL
from noticias_phb.items import NewsItem
from noticias_phb.pipelines import BaseNewsPipeline
from noticias_phb.settings import (
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
    TELEGRAM_CHAT_ID,
    TELEGRAM_MAX_CONTENT_SIZE,
    TELEGRAM_BOT_TOKENS,
)


class TelegramPipeline(BaseNewsPipeline):
    emoji = emojize(":newspaper:")

    @property
    def options(self):
        return {
            "session": MemorySession(),
            "api_id": TELEGRAM_API_ID,
            "api_hash": TELEGRAM_API_HASH,
        }

    async def telegram_client(self, token: str) -> TelegramClient:
        client = TelegramClient(**self.options)
        return await client.start(bot_token=token)

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
        return [
            [Button.url("Acessar publicação", adapter.get("link"))],
            [Button.url("Compartilhar no Whatsapp", self.whatsapp_link(adapter))],
        ]

    async def send_images(
        self, telegram: TelegramClient, adapter: ItemAdapter, message: str
    ):
        images = adapter.get("images")

        try:
            if len(images) > 1:
                await telegram.send_file(
                    entity=TELEGRAM_CHAT_ID,
                    file=images[1:10],
                )

        except FloodWaitError as exc:
            raise exc

        except RPCError as exc:
            self.logger.error(str(exc), exc_info=True)

        finally:
            await telegram.send_file(
                entity=TELEGRAM_CHAT_ID,
                file=images[0],
                caption=message,
                buttons=self.buttons(adapter),
            )

    async def send_video(
        self, telegram: TelegramClient, adapter: ItemAdapter, message: str
    ):
        tempdir = TemporaryDirectory()

        try:
            filepath = tempdir.name + "/%(id)s.%(ext)s"
            options = {"format": "best[height<=360]", "outtmpl": filepath}
            with YoutubeDL(options) as ytdl:
                ytdl.download(adapter.get("video"))

            for file in Path(tempdir.name).iterdir():
                await telegram.send_file(
                    entity=TELEGRAM_CHAT_ID,
                    file=str(file),
                    caption=message,
                    buttons=self.buttons(adapter),
                )

        except FloodWaitError as exc:
            raise exc

        except RPCError:
            await telegram.send_message(
                entity=TELEGRAM_CHAT_ID,
                message=message,
                buttons=self.buttons(adapter),
            )

        finally:
            tempdir.cleanup()

    async def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        message_text = self.message_text(adapter)

        for index, token in enumerate(TELEGRAM_BOT_TOKENS):
            try:
                telegram = await self.telegram_client(token)

                sleep(5)  # Blocking to avoid to FloodError
                if adapter.get("video"):
                    await self.send_video(telegram, adapter, message_text)

                elif adapter.get("images"):
                    await self.send_images(telegram, adapter, message_text)

                else:
                    await telegram.send_message(
                        entity=TELEGRAM_CHAT_ID,
                        message=message_text,
                        link_preview=False,
                        buttons=self.buttons(adapter),
                    )

            except FloodWaitError as exc:
                self.logger.warning(str(exc))
                if (index + 1) < len(TELEGRAM_BOT_TOKENS):
                    continue
                sleep(exc.seconds)  # Blocking to stop thread
                raise exc

            except Exception as exc:
                self.logger.critical(str(exc), exc_info=True)
                raise exc

            else:
                return item
