import re

from scrapy.item import Item, Field
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Identity

from noticias_phb.utils import clean_string



class NewsItem(Item):
    title = Field()
    images = Field()
    video = Field()
    content = Field()
    link = Field()
    posted_at = Field()


class NewsLoader(ItemLoader):
    default_item_class = NewsItem
    default_input_processor = MapCompose(clean_string)
    default_output_processor = TakeFirst()
    images_out = Identity()
    content_out = Identity()

    @staticmethod
    def images_in(values: list[str] | None):
        if values is None:
            return []
        
        keystrings = ['icon', 'demo-image', 'agenciabrasil']
        regex = '|'.join(keystrings)

        for value in values:
            if not value.startswith('http'):
                continue
            if re.search(regex, value) is None:
                yield value

    @staticmethod
    def content_in(values: list[str] | None):
        if values is None:
            return []
        
        keystrings = ['foto', 'fonte']
        regex = '|'.join(keystrings)
        
        for value in values:
            cleaned_str = clean_string(value)
            caption = re.search(regex, cleaned_str, re.IGNORECASE)
            if cleaned_str and caption is None:
                yield cleaned_str
