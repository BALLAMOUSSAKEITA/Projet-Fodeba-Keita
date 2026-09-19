from app.core.config import _normalize_database_url


def test_normalize_railway_database_url():
    url = "postgresql://user:pass@containers-us-west-123.railway.app:5432/railway"
    assert _normalize_database_url(url) == (
        "postgresql+asyncpg://user:pass@containers-us-west-123.railway.app:5432/railway"
    )


def test_normalize_postgres_scheme():
    url = "postgres://user:pass@host:5432/db"
    assert _normalize_database_url(url).startswith("postgresql+asyncpg://")
