from scrapy.item import Item, Field


class NewsItem(Item):
    posted_at = Field()
    link = Field()
    title = Field()
    content = Field()
    images = Field()
    videos = Field()
    external_videos = Field()
    youtube = Field()
    instagram = Field()
