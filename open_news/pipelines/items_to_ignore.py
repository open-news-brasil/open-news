from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from open_news.items import NewsItem
from open_news.pipelines import BaseNewsPipeline


class ItemsToIgnorePipeline(BaseNewsPipeline):
    key_strings = [
        "Praiana Med",
        "CASA DA INFORMÁTICA",
        "DonaMana",
        "ARROZ LONGÁ",
        "OFERTAS",
        "ARMAZÉM PARAÍBA",
        "ESPECIALIDADES: Hospital Marques Basto",
        "Clinica Viva",
        "Consultas e Exames",
        "PARNAUTO HONDA",
        "Mesquita Variedades",
        "TELNORTE",
        "Lojas Mesquita",
        "LENO CALÇADOS",
        "Casa do Pintor",
        "Promoção",
    ]

    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        title: str = adapter.get("title")

        for sub_string in self.key_strings:
            if sub_string.lower() in title.lower():
                raise DropItem(item)

        return item
