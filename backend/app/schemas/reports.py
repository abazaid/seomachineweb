from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReportCreateRequest(BaseModel):
    days: int = 30


class ReportResponse(BaseModel):
    id: int
    report_type: str
    status: str
    days: int
    markdown_path: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportDetailResponse(ReportResponse):
    result_json: str | None = None
