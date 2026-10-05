from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    classes,
    comptabilite,
    eleves,
    emploi_du_temps,
    health,
    paiements,
    paie,
    parametrage,
    personnel,
    rapports,
    roles,
    sync,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["santé"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
api_router.include_router(users.router, prefix="/users", tags=["utilisateurs"])
api_router.include_router(roles.router, prefix="/roles", tags=["rôles"])
api_router.include_router(parametrage.router, prefix="/parametrage", tags=["paramétrage"])
api_router.include_router(eleves.router, prefix="/eleves", tags=["élèves"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(personnel.router, prefix="/personnel", tags=["personnel"])
api_router.include_router(
    emploi_du_temps.router,
    prefix="/emploi-du-temps",
    tags=["emploi du temps"],
)
api_router.include_router(paiements.router, prefix="/paiements", tags=["paiements"])
api_router.include_router(paie.router, prefix="/paie", tags=["paie"])
api_router.include_router(comptabilite.router, prefix="/comptabilite", tags=["comptabilité"])
api_router.include_router(rapports.router, prefix="/rapports", tags=["rapports"])
api_router.include_router(sync.router, prefix="/sync", tags=["synchronisation"])
