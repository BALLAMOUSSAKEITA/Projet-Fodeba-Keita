from app.core.security import hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("admin123")
    assert hashed.startswith("$2b$")
    assert verify_password("admin123", hashed)
    assert not verify_password("wrong", hashed)
