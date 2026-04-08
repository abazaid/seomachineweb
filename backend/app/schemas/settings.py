from pydantic import BaseModel


class SettingsUpsertRequest(BaseModel):
    ga4_property_id: str | None = None
    gsc_site_url: str | None = None
    dataforseo_login: str | None = None
    dataforseo_password: str | None = None
    ai_provider: str | None = None
    ai_api_key: str | None = None


class SettingsResponse(BaseModel):
    ga4_property_id: str | None = None
    gsc_site_url: str | None = None
    dataforseo_login_masked: str | None = None
    dataforseo_password_masked: str | None = None
    ai_provider: str | None = None
    ai_api_key_masked: str | None = None
