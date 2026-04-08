from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskCreateFromReportResponse(BaseModel):
    created_count: int


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority_score: int
    keyword: str | None = None
    page_url: str | None = None
    source_type: str
    source_reference: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskStatusUpdateRequest(BaseModel):
    status: str
