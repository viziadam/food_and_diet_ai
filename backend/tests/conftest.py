import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB = Path(__file__).parent / "test.db"
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["AUTO_CREATE_SCHEMA"] = "true"
os.environ["SEED_DEMO_DATA"] = "true"

from app.core.config import get_settings  # noqa: E402

get_settings.cache_clear()

from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def remove_test_db() -> Generator[None, None, None]:
    TEST_DB.unlink(missing_ok=True)
    yield
    TEST_DB.unlink(missing_ok=True)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
