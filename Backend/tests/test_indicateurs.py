"""
Tests pour les endpoints d'indicateurs calcules.
"""


def test_indicateurs_national(client):
    """GET /indicateurs/national doit retourner les 5 KPI."""
    response = client.get("/indicateurs/national")
    assert response.status_code == 200
    data = response.json()

    # Verifier la presence des champs
    assert "taux_reussite_national" in data
    assert "ips_moyen_national" in data
    assert "nb_academies" in data
    assert "nb_lycees" in data
    assert "annee" in data

    # Verifier la coherence des valeurs
    assert 0 <= data["taux_reussite_national"] <= 100
    assert data["nb_academies"] > 0
    assert data["nb_lycees"] > 0


def test_indicateurs_academies(client):
    """GET /indicateurs/academies doit retourner une liste."""
    response = client.get("/indicateurs/academies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_correlation_points(client):
    """GET /indicateurs/correlation : chaque point doit avoir x et y."""
    response = client.get("/indicateurs/correlation")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for point in data:
        assert "ips" in point
        assert "taux_reussite" in point
        assert point["ips"] is not None
        assert point["taux_reussite"] is not None


def test_evolution(client):
    """GET /indicateurs/evolution doit retourner une liste triee par annee."""
    response = client.get("/indicateurs/evolution")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    # Verifier que c'est trie par annee croissante
    if len(data) > 1:
        annees = [d["annee"] for d in data]
        assert annees == sorted(annees)


def test_top_academies(client):
    """GET /indicateurs/top-academies?n=3 doit retourner exactement 3 elements."""
    response = client.get("/indicateurs/top-academies?critere=ips&n=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


def test_comparateur(client):
    """GET /indicateurs/comparateur doit comparer 2 academies."""
    all_acads = client.get("/academies/").json()
    if len(all_acads) < 2:
        return

    id_a = all_acads[0]["idacademie"]
    id_b = all_acads[1]["idacademie"]

    response = client.get(f"/indicateurs/comparateur?acad_a={id_a}&acad_b={id_b}")
    assert response.status_code == 200
    data = response.json()
    assert "academie_a" in data
    assert "academie_b" in data
    assert data["academie_a"]["idacademie"] == id_a
    assert data["academie_b"]["idacademie"] == id_b