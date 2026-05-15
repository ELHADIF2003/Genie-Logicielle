"""
Tests pour les endpoints /academies/...
"""


def test_list_academies(client):
    """GET /academies/ doit retourner une liste."""
    response = client.get("/academies/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Chaque academie doit avoir les bons champs
    assert "idacademie" in data[0]
    assert "nomacademie" in data[0]


def test_get_academie_by_id(client):
    """GET /academies/{id} doit retourner une academie."""
    # On recupere d'abord la liste pour avoir un ID valide
    all_acads = client.get("/academies/").json()
    if not all_acads:
        return  # skip si BDD vide

    valid_id = all_acads[0]["idacademie"]
    response = client.get(f"/academies/{valid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["idacademie"] == valid_id


def test_get_academie_not_found(client):
    """GET /academies/99999 doit retourner 404."""
    response = client.get("/academies/99999")
    assert response.status_code == 404


def test_get_resultats_bac(client):
    """GET /academies/{id}/resultats-bac doit retourner les resultats."""
    all_acads = client.get("/academies/").json()
    if not all_acads:
        return

    valid_id = all_acads[0]["idacademie"]
    response = client.get(f"/academies/{valid_id}/resultats-bac")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_resultats_bac_filter_annee(client):
    """Le filtre annee doit fonctionner."""
    all_acads = client.get("/academies/").json()
    if not all_acads:
        return

    valid_id = all_acads[0]["idacademie"]
    response = client.get(f"/academies/{valid_id}/resultats-bac?annee=2024")
    assert response.status_code == 200
    data = response.json()
    # Toutes les lignes doivent avoir annee=2024
    for ligne in data:
        assert ligne["annee"] == 2024