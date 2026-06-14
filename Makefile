.PHONY: backend frontend test lint dev

backend:
	cd backend && uv run fastapi dev app/main.py

frontend:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest
	cd frontend && npm run test -- --run

lint:
	cd backend && uv run ruff check . && uv run mypy app
	cd frontend && npm run lint

dev:
	docker compose up --build
