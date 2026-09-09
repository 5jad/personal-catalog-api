Design decisions and architecture notes

- FastAPI app with SQLAlchemy ORM and Alembic for migrations.
- Auth: JWT (symmetric secret), short-lived access tokens.
- Exports: FastAPI BackgroundTasks for now (simple, no external broker). Files saved under /tmp/exports in container — DESIGN.md will include tradeoffs and future extension (Celery/Redis).
- Database models: users, warehouses, products, export_jobs.

See the project README for running instructions.
