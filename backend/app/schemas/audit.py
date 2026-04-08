from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: str
    details: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
