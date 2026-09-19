import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.db.seed import run_seed
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        await run_seed(session)
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_token(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@fodebakeita.gn", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def teacher_token(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "enseignant@fodebakeita.gn", "password": "enseignant123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def directeur_token(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "directeur@fodebakeita.gn", "password": "directeur123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
