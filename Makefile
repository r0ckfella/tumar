# makefile
# I decided to use Makefile since it is widespread and does not depend on the technology
# stack being used.
# usage: make <command>
# for example: `make start-compose` executes `docker-compose up -d`

.PHONY: start-compose stop-compose ssh-nginx ssh-django ssh-worker check-network-config-details build-django-app start-db-conda start-dev deploy
start-compose:
	@echo '--- Starting the updated app in the background...'
	@export CURRENT_UID=$(id -u):$(id -g); \
	docker-compose up -d

stop-compose:
	@echo '--- Stopping the app...'
	@docker-compose down

ssh-nginx:
	@docker exec -it web bash

ssh-django:
	@docker exec -it app bash

ssh-worker:
	@docker exec -it worker bash

check-network-config-details:
	@docker network inspect tumar

build-django-app:
	@echo '--- Building the app with the new updates...'
	@docker build -t tumar/app:latest .

start-db-conda:
	@echo '--- Turning on postgres database in the conda development environment...'
	pg_ctl -D ./pgdata/ start

start-dev: start-db-conda
	@python manage.py migrate
	python manage.py runserver 0.0.0.0:8000

pull:
	@echo '--- Pulling the app updates from the repository...'
	@git pull

deploy: stop-compose build-django-app start-compose
