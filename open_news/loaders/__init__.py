import re

from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Identity

from open_news.items import NewsItem
from open_news.utils import clean_string


class NewsLoader(ItemLoader):
    default_item_class = NewsItem
    default_input_processor = MapCompose(clean_string)
    default_output_processor = Identity()
    posted_at_out = TakeFirst()
    link_out = TakeFirst()
    title_out = TakeFirst()

    @staticmethod
    def youtube_in(values: list[str] | None):
        if values is None:
            return

        for value in values:
            _, path = value.split("embed/")
            video_id, _ = path.split("?")
            yield "https://www.youtube.com/watch?v=" + video_id

    @staticmethod
    def instagram_in(values: list[str] | None):
        if values is None:
            return

        for value in values:
            publication, _ = value.split("/embed")
            yield publication

    @staticmethod
    def images_in(values: list[str] | None):
        if values is None:
            return

        keystrings = ["icon", "demo-image", "agenciabrasil", "gravatar"]
        regex = "|".join(keystrings)

        for value in values:
            if not value.startswith("http"):
                continue
            if re.search(regex, value) is None:
                yield value

    @staticmethod
    def content_in(values: list[str] | None):
        if values is None:
            return

        keystrings = ["foto", "fonte"]
        regex = "|".join(keystrings)

        for value in values:
            cleaned_str = clean_string(value)
            caption = re.search(regex, cleaned_str, re.IGNORECASE)
            if cleaned_str and caption is None:
                yield cleaned_str
