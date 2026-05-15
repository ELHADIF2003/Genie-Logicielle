"""
Tests basiques : endpoint racine, sante de l'application.
"""


def test_read_root(client):
    """L'endpoint / doit retourner 200 avec un message de bienvenue."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_docs_accessible(client):
    """La doc Swagger doit etre accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Le schema OpenAPI doit etre genere correctement."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    # On doit avoir au moins une vingtaine d'endpoints
    assert len(data["paths"]) > 15