DATA = data
SPIDERS = $(shell scrapy list)

data:
	$(foreach spider,$(SPIDERS),scrapy crawl $(spider) -O $(DATA)/$(spider).json;)
