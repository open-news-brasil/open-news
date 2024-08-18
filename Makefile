REQUIREMENTS = requirements.txt
IMAGE_NAME = noticias_phb


requirements:
	@poetry export --without-hashes --without=dev > $(REQUIREMENTS)

build: requirements
	@docker system prune -f
	@docker build --no-cache -t $(IMAGE_NAME):latest .
	@docker system prune -f
