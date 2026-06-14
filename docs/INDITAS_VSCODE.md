# Az alkalmazás elindítása Visual Studio Code-ban

Ez az útmutató Windows, Visual Studio Code, Docker Desktop, Python 3.12, `uv` és Node.js 22 használatára készült.

## 1. A projekt megnyitása

1. Indítsd el a Visual Studio Code-ot.
2. Válaszd a **File > Open Folder** menüpontot.
3. Nyisd meg a `food_and_diet_ai` projekt gyökérmappáját.
4. A VS Code felső menüjében válaszd a **Terminal > New Terminal** menüpontot.

A projekt futtatásához három külön terminált használunk:

- 1. terminál: PostgreSQL adatbázis
- 2. terminál: FastAPI backend
- 3. terminál: React frontend

## 2. Környezeti változók létrehozása

A projekt gyökérmappájában másold le a `.env.example` fájlt `.env` néven.

CMD terminálban:

```cmd
copy .env.example .env
```

A létrejött `.env` fájl alapértelmezett adatbázis-kapcsolata:

```text
postgresql+psycopg://food_ai:food_ai@localhost:5432/food_ai
```

## 3. Első terminál: az adatbázis indítása

A terminál munkakönyvtára a projekt gyökere legyen.

```cmd
docker compose up -d db
```

Ellenőrzés:

```cmd
docker compose ps
```

A `db` szolgáltatás állapota néhány másodperc után `healthy` legyen.

Az adatbázis leállítása:

```cmd
docker compose stop db
```

Az adatbázis és a tárolt adatok teljes törlése csak akkor szükséges, ha teljesen új adatbázist szeretnél:

```cmd
docker compose down -v
```

Figyelem: a `-v` kapcsoló törli a PostgreSQL adatokat.

## 4. Második terminál: a backend indítása

Nyiss egy új VS Code terminált, majd:

```cmd
cd backend
```

Első indításkor vagy függőségváltozás után:

```cmd
uv sync --extra dev
```

Adatbázis-migrációk futtatása:

```cmd
uv run alembic upgrade head
```

Backend indítása fejlesztői módban:

```cmd
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Ellenőrzési címek:

- API állapot: `http://localhost:8000/api/v1/health`
- Swagger dokumentáció: `http://localhost:8000/docs`

A backend leállítása: `Ctrl + C`.

## 5. Harmadik terminál: a frontend indítása

Nyiss egy harmadik VS Code terminált, majd:

```cmd
cd frontend
```

Első indításkor vagy a `package-lock.json` változása után:

```cmd
npm ci
```

Frontend indítása:

```cmd
npm run dev
```

Az alkalmazás címe:

```text
http://localhost:5173
```

A frontend leállítása: `Ctrl + C`.

## 6. A fejlesztői ág működésének ellenőrzése

### Backend ellenőrzések

A `backend` mappában:

```cmd
uv run ruff check .
uv run mypy app
uv run pytest
```

### Frontend ellenőrzések

A `frontend` mappában:

```cmd
npm run lint
npm run test -- --run
npm run build
```

Csak akkor egyesítsd a fejlesztői ágat a `master` ágba, ha minden parancs hibamentesen lefut, az alkalmazás megnyílik, és a GitHub pull request ellenőrzései zöldek.

## 7. Gyors napi indítás

Ha a függőségek már telepítve vannak, a napi indításhoz elegendő:

**1. terminál, projekt gyökere:**

```cmd
docker compose up -d db
```

**2. terminál:**

```cmd
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**3. terminál:**

```cmd
cd frontend
npm run dev
```

## 8. SQLite használata Docker nélkül

Ha átmenetileg nem szeretnél PostgreSQL-t indítani, a backend alapértelmezés szerint SQLite adatbázist is tud használni. Ehhez a `backend` mappában hozz létre egy `.env` fájlt ezzel a tartalommal:

```text
DATABASE_URL=sqlite:///./food_and_diet_ai.db
AUTO_CREATE_SCHEMA=true
SEED_DEMO_DATA=true
CORS_ORIGINS=["http://localhost:5173"]
```

Ezután a backend indítása ugyanaz. Hosszabb távú fejlesztéshez a PostgreSQL használata javasolt.
