from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContentCreateRequest(BaseModel):
    keyword: str
    title: str


class ContentOut(BaseModel):
    id: int
    keyword: str
    title: str
    status: str
    current_version: int
    latest_body: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContentActionRequest(BaseModel):
    notes: str | None = None


class ContentVersionOut(BaseModel):
    version_number: int
    stage: str
    body: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
