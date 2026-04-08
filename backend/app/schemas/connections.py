from pydantic import BaseModel


class ProviderStatus(BaseModel):
    provider: str
    status: str
    message: str


class ConnectionTestResponse(BaseModel):
    providers: list[ProviderStatus]
