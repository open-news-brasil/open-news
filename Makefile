REQUIREMENTS = requirements.txt
IMAGE_NAME = open-news-brasil


requirements:
	@poetry export --without-hashes --without=dev > $(REQUIREMENTS)

build: requirements
	@docker build --no-cache -t $(IMAGE_NAME):latest .
