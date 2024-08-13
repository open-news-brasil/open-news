import scrapy


class PostItem(scrapy.Item):
    title = scrapy.Field()
    image = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()
    posted_at = scrapy.Field()
