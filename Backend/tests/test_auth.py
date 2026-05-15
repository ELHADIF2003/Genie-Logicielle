"""
Tests pour l'authentification (login, JWT, protection des routes).
"""


def test_login_wrong_password(client):
    """Un mauvais MDP doit retourner 401."""
    response = client.post(
        "/auth/login",
        json={"email": "admin@projet.fr", "password": "wrong_password"},
    )
    assert response.status_code == 401


def test_login_invalid_email_format(client):
    """Un email invalide doit retourner 422 (validation Pydantic)."""
    response = client.post(
        "/auth/login",
        json={"email": "pas_un_email", "password": "azerty123"},
    )
    assert response.status_code == 422


def test_login_unknown_user(client):
    """Un email inconnu doit retourner 401."""
    response = client.post(
        "/auth/login",
        json={"email": "n_existe_pas@projet.fr", "password": "azerty123"},
    )
    assert response.status_code == 401


def test_login_success_and_token(client, admin_token):
    """Le login admin doit retourner un access_token."""
    assert admin_token is not None
    assert isinstance(admin_token, str)
    assert len(admin_token) > 50  # un JWT fait au moins ca


def test_protected_route_without_token(client):
    """Une route admin sans token doit retourner 401."""
    response = client.get("/admin/stats")
    assert response.status_code == 401


def test_protected_route_with_bad_token(client):
    """Une route admin avec un token bidon doit retourner 401."""
    response = client.get(
        "/admin/stats",
        headers={"Authorization": "Bearer ce_token_n_existe_pas"},
    )
    assert response.status_code == 401


def test_admin_stats_with_token(client, admin_headers):
    """Avec un token admin valide, /admin/stats doit fonctionner."""
    response = client.get("/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "nb_academies" in data
    assert "nb_lycees" in data


def test_me_with_token(client, admin_headers):
    """GET /auth/me avec token doit retourner l'utilisateur courant."""
    response = client.get("/auth/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"