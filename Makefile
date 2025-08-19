.PHONY: help build up down logs shell clean install dev db-up init-db load-data test lint format

help:
	@echo "Available commands:"
	@echo "  build      - Build the Docker image"
	@echo "  up         - Start the application with docker-compose"
	@echo "  down       - Stop the application"
	@echo "  logs       - View application logs"
	@echo "  shell      - Open a shell in the web container"
	@echo "  clean      - Remove containers and volumes"
	@echo "  install    - Install dependencies locally (in .venv)"
	@echo "  db-up      - Start only the database container"
	@echo "  dev        - Run in development mode locally (starts db automatically)"
	@echo "  init-db    - Initialize database (Docker)"
	@echo "  load-data  - Load all data from GitHub (Docker)"
	@echo "  test       - Run tests (Docker)"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code with black and isort"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec web bash

clean:
	docker compose down -v
	docker system prune -f

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

db-up:
	docker compose up -d db

dev: db-up
	@echo "Starting local development server with PostgreSQL container"
	source .venv/bin/activate && export FLASK_APP=wsgi.py && export DATABASE_URL=postgresql://tacofancy:tacofancy@localhost:5432/tacofancy && flask run --host=0.0.0.0 --port=5000

init-db: up
	docker compose exec web flask init-db

load-data: up
	docker compose exec web flask load-all

test: up
	docker compose exec web flask test

lint:
	.venv/bin/flake8 .
	.venv/bin/black --check .
	.venv/bin/isort --check-only .

format:
	.venv/bin/black .
	.venv/bin/isort .