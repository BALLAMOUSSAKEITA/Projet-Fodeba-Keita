from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.role import Permission, Role

ROLES = [
    {
        "code": "super_admin",
        "label": "Super administrateur",
        "description": "Administration complète de la plateforme",
        "permissions": ["*"],
    },
    {
        "code": "directeur",
        "label": "Directeur / Promoteur",
        "description": "Validation et pilotage de l'établissement",
        "permissions": [
            "users.manage",
            "users.create",
            "students.enroll",
            "students.view",
            "grades.validate_bulletins",
            "payments.collect",
            "expenses.validate",
            "payroll.generate",
            "payroll.view",
            "reports.view",
            "reports.view_pedagogical",
            "payments.view",
            "settings.manage",
            "personnel.view",
            "personnel.manage",
            "timetable.view",
            "timetable.manage",
            "attendance.manage",
            "attendance.view",
            "communication.manage",
            "communication.view",
            "security.audit",
        ],
    },
    {
        "code": "secretaire",
        "label": "Secrétaire / Scolarité",
        "description": "Inscriptions et dossiers élèves",
        "permissions": [
            "users.create",
            "students.enroll",
            "students.view",
            "payments.collect",
            "reports.view_pedagogical",
            "settings.view",
            "personnel.view",
            "timetable.view",
            "grades.modify",
            "attendance.view",
            "communication.manage",
            "communication.view",
        ],
    },
    {
        "code": "econome",
        "label": "Économe / Comptable",
        "description": "Gestion financière",
        "permissions": [
            "payments.collect",
            "expenses.create",
            "payroll.generate",
            "payroll.view",
            "reports.view",
        ],
    },
    {
        "code": "enseignant",
        "label": "Enseignant",
        "description": "Saisie notes et présences",
        "permissions": [
            "grades.modify",
            "grades.view_own",
            "students.view",
            "timetable.view",
            "attendance.manage",
            "payroll.view",
        ],
    },
    {
        "code": "surveillant",
        "label": "Surveillant / Discipline",
        "description": "Suivi absences et discipline",
        "permissions": ["attendance.manage", "attendance.view", "grades.view_own", "students.view"],
    },
    {
        "code": "parent",
        "label": "Parent / Tuteur",
        "description": "Consultation dossier enfant",
        "permissions": ["grades.view_own", "communication.view", "parent.portal"],
    },
]

PERMISSIONS = [
    ("users.manage", "Gérer les utilisateurs", "auth"),
    ("users.create", "Créer des comptes utilisateurs", "auth"),
    ("students.enroll", "Inscrire un élève", "students"),
    ("students.view", "Consulter les dossiers élèves", "students"),
    ("grades.modify", "Modifier les notes", "grades"),
    ("grades.validate_bulletins", "Valider les bulletins", "grades"),
    ("grades.view_own", "Consulter ses notes", "grades"),
    ("payments.collect", "Encaisser les paiements", "finance"),
    ("payments.view", "Consulter les paiements", "finance"),
    ("expenses.create", "Saisir une dépense", "finance"),
    ("expenses.validate", "Valider une dépense", "finance"),
    ("payroll.generate", "Générer la paie", "finance"),
    ("payroll.view", "Consulter la paie", "finance"),
    ("reports.view", "Consulter les rapports", "reports"),
    ("reports.view_pedagogical", "Consulter les rapports pédagogiques", "reports"),
    ("attendance.manage", "Gérer les présences", "attendance"),
    ("attendance.view", "Consulter les présences", "attendance"),
    ("settings.manage", "Gérer le paramétrage de l'établissement", "settings"),
    ("settings.view", "Consulter le paramétrage", "settings"),
    ("personnel.view", "Consulter le personnel", "personnel"),
    ("personnel.manage", "Gérer le personnel", "personnel"),
    ("timetable.view", "Consulter l'emploi du temps", "timetable"),
    ("timetable.manage", "Gérer l'emploi du temps", "timetable"),
    ("communication.manage", "Gérer les annonces et communications", "communication"),
    ("communication.view", "Consulter les annonces", "communication"),
    ("parent.portal", "Accéder au portail parent", "communication"),
    ("security.audit", "Consulter le journal d'audit et l'historique", "security"),
]

DEFAULT_USERS = [
    {
        "email": "admin@fodebakeita.gn",
        "password": "admin123",
        "nom": "Administrateur",
        "prenom": "SGEP",
        "telephone": "+224620000001",
        "role_code": "super_admin",
    },
    {
        "email": "directeur@fodebakeita.gn",
        "password": "directeur123",
        "nom": "Keita",
        "prenom": "Directeur",
        "telephone": "+224620000002",
        "role_code": "directeur",
    },
    {
        "email": "enseignant@fodebakeita.gn",
        "password": "enseignant123",
        "nom": "Diallo",
        "prenom": "Enseignant",
        "telephone": "+224620000003",
        "role_code": "enseignant",
    },
]


async def seed_permissions(db: AsyncSession) -> dict[str, Permission]:
    permission_map: dict[str, Permission] = {}
    for code, description, module in PERMISSIONS:
        result = await db.execute(select(Permission).where(Permission.code == code))
        permission = result.scalar_one_or_none()
        if permission is None:
            permission = Permission(code=code, description=description, module=module)
            db.add(permission)
        permission_map[code] = permission
    await db.flush()
    return permission_map


async def seed_roles(db: AsyncSession, permission_map: dict[str, Permission]) -> dict[str, Role]:
    role_map: dict[str, Role] = {}
    all_permissions = list(permission_map.values())

    for role_data in ROLES:
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.code == role_data["code"])
        )
        role = result.scalar_one_or_none()
        perms = (
            all_permissions
            if role_data["permissions"] == ["*"]
            else [permission_map[code] for code in role_data["permissions"]]
        )

        if role is None:
            role = Role(
                code=role_data["code"],
                label=role_data["label"],
                description=role_data["description"],
                is_system=True,
                permissions=perms,
            )
            db.add(role)
            await db.flush()
        else:
            role.permissions.clear()
            role.permissions.extend(perms)

        role_map[role_data["code"]] = role

    await db.flush()
    return role_map


async def seed_default_users(db: AsyncSession, role_map: dict[str, Role]) -> None:
    from app.models.user import User

    for user_data in DEFAULT_USERS:
        result = await db.execute(select(User).where(User.email == user_data["email"]))
        if result.scalar_one_or_none() is not None:
            continue

        db.add(
            User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                nom=user_data["nom"],
                prenom=user_data["prenom"],
                telephone=user_data["telephone"],
                role_id=role_map[user_data["role_code"]].id,
                is_active=True,
            )
        )


async def run_seed(db: AsyncSession) -> None:
    from app.db.seed_parametrage import seed_parametrage
    from app.db.seed_competences import seed_competences
    from app.db.seed_edt import seed_edt
    from app.db.seed_notes import seed_notes
    from app.db.seed_personnel import seed_personnel
    from app.db.seed_paiements import seed_paiements
    from app.db.seed_paie import seed_paie
    from app.db.seed_comptabilite import seed_comptabilite
    from app.db.seed_communication import seed_communication

    permission_map = await seed_permissions(db)
    role_map = await seed_roles(db, permission_map)
    await seed_default_users(db, role_map)
    await seed_parametrage(db)
    await seed_personnel(db)
    await seed_edt(db)
    await seed_notes(db)
    await seed_competences(db)
    await seed_paiements(db)
    await seed_paie(db)
    await seed_comptabilite(db)
    await seed_communication(db)
    await db.commit()
