import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# Import models so their tables register on Base.metadata before create_all.
# (database.py normally does this lazily inside init_db(), but tests need
# it eagerly since we call create_all() ourselves.)
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.search_history import SearchHistory

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fresh in-memory DB per test function — no state leaks between tests."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Unauthenticated TestClient with the real DB swapped for the test DB."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_credentials():
    """Reusable fake user credentials for registration/login tests."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "StrongPass123!",
    }


@pytest.fixture(scope="function")
def authenticated_client(client, test_user_credentials):
    """
    A TestClient that's already registered a user and carries a valid
    Bearer token — use this for any test that hits a protected route.
    """
    client.post("/api/auth/register", json=test_user_credentials)

    login_resp = client.post(
        "/api/auth/login",
        data={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"],
        },
    )
    token = login_resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client