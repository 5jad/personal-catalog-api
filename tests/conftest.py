import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Before importing the app, set a test DATABASE_URL so modules that read settings will be consistent.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")

from app.main import app
import app.db.session as db_session
from app.models import Base

# Create a new SQLite test database
TEST_DB_URL = os.environ.get("DATABASE_URL")
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Replace the SessionLocal used by the application modules so background tasks use the test DB too.
db_session.engine = engine
db_session.SessionLocal = TestingSessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def cleanup_db():
    # Truncate tables between tests for isolation
    yield
    conn = engine.connect()
    trans = conn.begin()
    for table in reversed(Base.metadata.sorted_tables):
        conn.execute(table.delete())
    trans.commit()
    conn.close()
