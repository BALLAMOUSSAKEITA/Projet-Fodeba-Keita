from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine, get_db
from app.models.eleve import Eleve
from app.models.user import User
from app.db.seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await run_seed(session)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de gestion scolaire — Groupe Scolaire Privé Fodeba Keita",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["racine"])
async def root():
    return {
        "message": "SGEP API — Groupe Scolaire Privé Fodeba Keita",
        "docs": "/docs",
        "version": "0.1.0",
    }


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics(db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    db_up = 1
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_up = 0

    eleves = (await db.execute(select(func.count()).select_from(Eleve))).scalar_one()
    users = (await db.execute(select(func.count()).select_from(User))).scalar_one()

    lines = [
        "# HELP sgep_up Disponibilité API SGEP (1=ok)",
        "# TYPE sgep_up gauge",
        f"sgep_up {db_up}",
        "# HELP sgep_database_up Connexion PostgreSQL",
        "# TYPE sgep_database_up gauge",
        f"sgep_database_up {db_up}",
        "# HELP sgep_eleves_total Nombre d'élèves inscrits",
        "# TYPE sgep_eleves_total gauge",
        f"sgep_eleves_total {eleves}",
        "# HELP sgep_users_total Nombre de comptes utilisateurs",
        "# TYPE sgep_users_total gauge",
        f"sgep_users_total {users}",
    ]
    return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4; charset=utf-8")
