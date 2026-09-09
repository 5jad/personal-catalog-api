Design decisions and architecture notes

- FastAPI app with SQLAlchemy ORM and Alembic for migrations.
- Auth: JWT (symmetric secret), short-lived access tokens.
- Exports: FastAPI BackgroundTasks for now (simple, no external broker). Files saved under configurable EXPORT_DIR in container — default /tmp/exports.

Export flow (Phase 6 details)
- Request flow:
  - Client POSTs to /warehouses/{id}/exports?format=csv|json authenticated as owner.
  - Server creates an ExportJob row with status `pending` and returns job metadata immediately (async acknowledgement).
  - A BackgroundTasks job runs _do_export(job_id, format) using a separate DB session (SessionLocal) to avoid leaking request-scoped sessions.

- Background job responsibilities:
  - Re-validate warehouse ownership before exporting (defense-in-depth in case of race conditions).
  - Query products for the warehouse and write either CSV or JSON to the EXPORT_DIR with a timestamped filename.
  - Update ExportJob status to `completed` and set file_path on success, or `failed` on exception.
  - Log errors and events for observability.

- Storage & Retention:
  - Current implementation stores files locally inside the container at EXPORT_DIR. This is simple and works for small deployments and testing.
  - For production we recommend:
    - Use object storage (S3, MinIO) for persisted/exported files.
    - Add retention policy and background cleanup job to delete old exports.
    - Make export file visibility configurable (signed URLs vs authenticated download endpoints).

- Scaling & Reliability:
  - BackgroundTasks is lightweight and runs in-process — good for low-volume exports. It does not support retries, distributed workers, or durable queues.
  - For higher reliability/scale migrate to Celery/RQ with Redis/RabbitMQ and run workers separately. This enables retry, monitoring, and backoff.

- Security:
  - Exports and download endpoints are protected by JWT + ownership checks; endpoints return 404 for resources the user does not own (defense-in-depth).

See TESTING.md for export lifecycle tests.
