from scrapy.item import Item, Field


class NewsItem(Item):
    title = Field()
    images = Field()
    video = Field()
    content = Field()
    link = Field()
    posted_at = Field()
