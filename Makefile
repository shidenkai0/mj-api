#!make
MAKEFLAGS += --silent

COMMIT_SHA=$(shell git rev-parse --short HEAD)
DOCKER_REGISTRY=registry.digitalocean.com/mmess
IMAGE_NAME=api
MIGRATION_IMAGE_NAME=api-migration

.PHONY: show_version \
		setup \
		migrate \
		seed_db \
		api_v1_gen \
		test \
		deploy \
		build_image \
		build_migration_image \
		build \
		push_image \
		push_migration_image \
		do_registry_login \
		update_requirements \
		sync_requirements \
		all


show_version:
	@echo ${COMMIT_SHA}

setup: # setup local development environment
	python3.11 -m venv .venv
	pip install pip-tools

deploy: # Deploy the app through Helm
	DOCKER_REGISTRY=${DOCKER_REGISTRY} \
	COMMIT_SHA=${COMMIT_SHA} \
	IMAGE_NAME=${IMAGE_NAME} \
	./deployment/bin/deploy.sh

build_image:
	docker build --no-cache --platform linux/amd64 -t ${IMAGE_NAME}:${COMMIT_SHA} .
	docker tag ${IMAGE_NAME}:${COMMIT_SHA} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${COMMIT_SHA}


build_migration_image:
	docker build -f Dockerfile.migrations --no-cache --platform linux/amd64 -t ${MIGRATION_IMAGE_NAME}:${COMMIT_SHA} .
	docker tag ${MIGRATION_IMAGE_NAME}:${COMMIT_SHA} ${DOCKER_REGISTRY}/${MIGRATION_IMAGE_NAME}:${COMMIT_SHA}

do_registry_login:
	 doctl registry login --expiry-seconds 600

push_image: do_registry_login
	docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${COMMIT_SHA}

push_migration_image: do_registry_login
	docker push ${DOCKER_REGISTRY}/${MIGRATION_IMAGE_NAME}:${COMMIT_SHA}

migrate:
	docker-compose run --rm web alembic upgrade head

migrate_test:
	docker compose up -d db
	docker-compose run --rm test wait-for-it db:5432 -- alembic upgrade head

migrate_prod:
	kubectl run migration -it --restart=Never --image ${DOCKER_REGISTRY}/${MIGRATION_IMAGE_NAME}:${COMMIT_SHA} --rm -- -database "${DATABASE_URL}" up

generate_migration:
	docker compose run web alembic revision --autogenerate -m "${desc}"

update_requirements:
	pip-compile requirements.in
	pip-compile requirements-dev.in

sync_dev_requirements:
	pip-sync requirements.txt requirements-dev.txt

sync_requirements:
	pip-sync requirements.txt

build_local:
	docker-compose build

seed_db: migrate
	docker-compose run -e PYTHONPATH=/app web python app/tools/seed_db.py

run:
	docker-compose run --service-ports web

test: migrate_test
	docker-compose run --rm test pytest -vv

dev_tunnel:
	ngrok http 8080

cleanup_supabase:
	docker-compose run --rm web alembic downgrade base
	docker-compose run -e PYTHONPATH=/app web python app/tools/seed_db.py --cleanup

cleanup:
	docker-compose down -v --remove-orphans

all: build_image build_migration_image push_image push_migration_image
