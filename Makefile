.PHONY: install dev backend test-backend lint-backend format-backend docker-up docker-down clean

install:
	python -m pip install -r backend/requirements.txt -r backend/requirements-dev.txt
	cd frontend && npm install

dev:
	cd frontend && npm run dev

backend:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

test-backend:
	cd backend && pytest

lint-backend:
	cd backend && black --check . && isort --check-only . && flake8 .

format-backend:
	cd backend && black . && isort .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find frontend -type d -name "dist" -prune -exec rm -rf {} +
