REQUIREMENTS = requirements.txt
IMAGE_NAME = noticias_phb


requirements:
	@poetry export --without-hashes --without=dev > $(REQUIREMENTS)

build: requirements
	@docker build --no-cache -t $(IMAGE_NAME):latest .
