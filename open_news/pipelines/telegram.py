import json

from uuid import uuid4

from boto3 import client
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from open_news.items import NewsItem
from open_news.pipelines import BaseNewsPipeline
from open_news.settings import (
    TELEGRAM_CHAT_ID,
    TELEGRAM_QUEUE_URL,
    TELEGRAM_QUEUE_REGION,
)


sqs = client("sqs", region_name=TELEGRAM_QUEUE_REGION)


class TelegramPipeline(BaseNewsPipeline):
    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        message = {
            "destiny": TELEGRAM_CHAT_ID,
            "title": adapter.get("title"),
            "link": adapter.get("link"),
            "content": adapter.get("content", []),
            "images": adapter.get("images", []),
            "videos": adapter.get("videos", []),
            "youtube": adapter.get("youtube", []),
            "instagram": adapter.get("instagram", []),
            "external_videos": adapter.get("external_videos", []),
        }

        try:
            sqs.send_message(
                QueueUrl=TELEGRAM_QUEUE_URL,
                MessageBody=json.dumps(message),
                MessageGroupId=str(uuid4()),
            )

        except Exception:
            raise DropItem(item)

        finally:
            return item
