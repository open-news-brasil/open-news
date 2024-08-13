import scrapy


class FolhaItem(scrapy.Item):
    title = scrapy.Field()
    image = scrapy.Field()
    content = scrapy.Field()
    link = scrapy.Field()
