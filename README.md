# Personal Catalog API

Simple FastAPI service for per-user warehouses (lists) and products (items).

Quick start

1. Copy .env.example to .env and fill values.
2. docker compose up --build
3. API will be available at http://localhost:8000

Project layout

- app/
  - main.py           # FastAPI app
  - core/             # configuration
  - db/               # database session
  - models.py         # SQLAlchemy models
  - schemas.py        # Pydantic schemas
  - routers/          # API routers (auth, warehouses, products, exports)
- alembic/            # alembic env (autogenerate)

See DESIGN.md and TESTING.md (to be added).
