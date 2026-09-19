from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    environment: str
    database: str
    redis: str


class MessageResponse(BaseModel):
    message: str
