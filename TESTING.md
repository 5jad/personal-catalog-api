# Tests for the Personal Catalog API

To run tests locally:

1. Copy the example env and set a test database (optional):
   cp .env.example .env

2. Install dev requirements (in the repo root):
   pip install -r requirements.txt
   pip install pytest httpx

3. Run pytest:
   pytest -q

Notes:
- Tests use a SQLite file database created under ./test.db by default and will create tables automatically.
- If you want to run tests against a PostgreSQL test database, set DATABASE_URL before running pytest.
