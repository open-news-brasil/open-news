from json import dumps as json_dumps
from pathlib import Path
from importlib import import_module


SPIDERS_PATH = Path(__file__).parent / "spiders"
IMPORT_PATH = "open_news.spiders.{}"
OUTPUT_FILE = "news_coverage.json"


def modules():
    for path in SPIDERS_PATH.glob("*.py"):
        if not path.name.startswith("__"):
            yield path.name.removesuffix(".py")


def sites() -> dict[str, dict[str, list[str]]]:
    collection: dict[str, dict[str, list[str]]] = {}
    for module in modules():
        spider = import_module(IMPORT_PATH.format(module))
        state, city = module.split("_", 1)
        collection[state] = {city: []}
        for member in dir(spider):
            if member.endswith("Spider"):
                spider_class = getattr(spider, member)
                if not hasattr(spider_class, "allowed_domains"):
                    continue
                collection[state][city].extend(getattr(spider_class, "allowed_domains"))
    return collection


if __name__ == "__main__":
    file = Path(OUTPUT_FILE)
    file.write_text(json_dumps(sites(), indent=4))
