from uuid import UUID

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: UUID
    code: str
    description: str
    module: str

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: UUID
    code: str
    label: str
    description: str | None
    is_system: bool
    permissions: list[PermissionResponse]

    model_config = {"from_attributes": True}
