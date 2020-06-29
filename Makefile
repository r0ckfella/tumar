# makefile
# I decided to use Makefile since it is widespread and does not depend on the technology
# stack being used.
# usage: make <command>
# for example: `make start-compose` executes `docker-compose up -d`

.PHONY: start-compose stop-compose ssh-nginx ssh-django ssh-worker check-network-config-details build-django-app export-curr-user start-db-conda start-dev deploy
start-compose:
	docker-compose up -d

stop-compose:
	@eval docker stop $$(docker ps -a -q)
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
	@docker build -t tumar/app:latest .

export-curr-user:
	@export CURRENT_UID=$(id -u):$(id -g)

start-db-conda:
	@echo 'Turning on postgres database in the conda development environment...'
	pg_ctl -D ./pgdata/ start

start-dev: start-db-conda
	@python manage.py migrate
	python manage.py runserver 0.0.0.0:8000

pull:
	git stash
	git pull

deploy: stop-compose build-django-app export-curr-user start-compose
