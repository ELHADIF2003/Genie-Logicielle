"""
Tests pour le module de securite (bcrypt + JWT).
Tests de logique pure, sans BDD.
"""
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_password_is_not_plain():
    """Le hash ne doit pas etre egal au mot de passe en clair."""
    password = "mon_mdp_secret"
    hashed = hash_password(password)
    assert hashed != password


def test_hash_password_is_bcrypt_format():
    """Le hash doit commencer par $2b$ (format bcrypt)."""
    hashed = hash_password("test123")
    assert hashed.startswith("$2b$")


def test_verify_correct_password():
    """verify_password doit accepter le bon MDP."""
    password = "azerty123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_wrong_password():
    """verify_password doit rejeter un mauvais MDP."""
    hashed = hash_password("azerty123")
    assert verify_password("wrong_password", hashed) is False


def test_hash_is_different_each_time():
    """Le meme MDP doit produire des hashs differents (grace au salt)."""
    password = "azerty123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2
    # Les deux doivent quand meme verifier le MDP
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_jwt_create_and_decode():
    """Un token cree puis decode doit contenir le bon subject."""
    token = create_access_token(subject="user@test.fr")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user@test.fr"


def test_jwt_extra_claims():
    """Les claims additionnels doivent etre presents dans le payload."""
    token = create_access_token(
        subject="user@test.fr",
        extra_claims={"role": "admin", "id": 42},
    )
    payload = decode_access_token(token)
    assert payload["role"] == "admin"
    assert payload["id"] == 42


def test_jwt_invalid_token():
    """Un token bidon doit retourner None."""
    payload = decode_access_token("ceci_n_est_pas_un_token")
    assert payload is None