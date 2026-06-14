# Food and Diet AI

API-first, modular meal-planning MVP for Hungarian users. The application generates a personalized one-day meal plan from a calorie target, household size, cuisine preferences, dietary constraints, cooking-time limit and budget. It returns recipes, portions, nutrition estimates, cooking instructions and an aggregated shopping list.

## Current MVP

- Weight-loss, conscious-eating and high-protein goals
- Hungarian, Italian and Mediterranean recipe categories
- Seasonal ingredient scoring for the current month
- Household-aware portions and estimated Hungarian prices
- Daily calorie and macro summary
- Aggregated shopping list
- Mobile-first responsive React interface
- FastAPI OpenAPI contract suitable for a later mobile application
- PostgreSQL in production, SQLite fallback for local tests
- Alembic database migrations and versioned schema
- Provider boundary for a later OpenAI or Ollama integration
- Docker Compose and GitHub Actions

## Architecture

```text
React web client
      |
      v
FastAPI REST API
      |
      +-- catalog module (ingredients and recipes)
      +-- planning module (filtering, scoring, portions)
      +-- pricing and nutrition calculations
      +-- persistence layer (SQLAlchemy)
      |
      v
PostgreSQL
```

The planner is deterministic. Language-model integration is intentionally kept behind a future provider interface so that numeric, allergen and budget calculations never depend on generated text.

## Local development

### Prerequisites

- Python 3.12
- Node.js 22+
- `uv`
- PostgreSQL, or use the default SQLite development database

### Backend

```bash
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

API documentation: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Application: `http://localhost:5173`

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Application: `http://localhost:3000`

## Tests and quality checks

```bash
cd backend
uv run pytest
uv run ruff check .
uv run mypy app

cd ../frontend
npm run test -- --run
npm run lint
npm run build
```

## Main API endpoints

- `GET /api/v1/health`
- `GET /api/v1/catalog/recipes`
- `POST /api/v1/plans/generate`
- `GET /api/v1/plans/{plan_id}`

## Extension path

The current `PlannerEngine` is replaceable. A later weekly optimizer can implement the same interface using OR-Tools without changing the API or UI. Planned modules include authentication, pantry inventory, sports nutrition, multi-store optimization, PDF exports and LLM-generated explanatory text.

## Health and pricing notice

The application provides household meal-planning estimates, not medical or dietetic treatment. Prices and nutrition values are estimates and must be reviewed before production use.
