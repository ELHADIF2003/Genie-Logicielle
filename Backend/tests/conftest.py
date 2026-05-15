"""
Fixtures pytest partagees entre tous les tests.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.crud import utilisateur as crud_user


@pytest.fixture(scope="session")
def client():
    """Client de test FastAPI, partage entre tous les tests."""
    return TestClient(app)


@pytest.fixture(scope="session")
def db_session():
    """Session BDD pour les tests qui en ont besoin."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def admin_token(client):
    """
    Recupere un token JWT admin.
    Suppose qu'un admin 'admin@projet.fr' existe deja en BDD.
    """
    response = client.post(
        "/auth/login",
        json={"email": "admin@projet.fr", "password": "azerty123"},
    )
    if response.status_code != 200:
        pytest.skip("Admin 'admin@projet.fr' / 'azerty123' inexistant en BDD. "
                    "Lance python -m app.scripts.create_admin")
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    """Headers HTTP avec le token admin."""
    return {"Authorization": f"Bearer {admin_token}"}