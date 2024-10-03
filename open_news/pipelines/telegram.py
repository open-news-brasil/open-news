import json

from uuid import uuid4
from boto3 import client
from itemadapter import ItemAdapter

from open_news.items import NewsItem
from open_news.pipelines import BaseNewsPipeline
from open_news.settings import TELEGRAM_CHAT_ID, TELEGRAM_QUEUE_URL


sqs = client("sqs")


class TelegramPipeline(BaseNewsPipeline):
    async def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        video_link = item.get("video")
        images_links = item.get("images")
        message = {
            "destiny": TELEGRAM_CHAT_ID,
            "title": adapter.get("title"),
            "link": adapter.get("link"),
            "content": adapter.get("content"),
            "images": images_links if images_links else [],
            "youtube": [video_link] if video_link else [],
        }

        try:
            sqs.send_message(
                QueueUrl=TELEGRAM_QUEUE_URL,
                MessageBody=json.dumps(message),
                MessageDeduplicationId=str(uuid4()),
                MessageGroupId=str(uuid4()),
            )

        except Exception as exc:
            raise exc

        finally:
            return item
