import os
import traceback

from sqlalchemy.orm import Session

from app.models.setting import SystemSetting
from app.services.settings_service import decrypt_value


def _get_setting(db: Session, key: str) -> str | None:
    record = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if record:
        try:
            return decrypt_value(record.value_encrypted)
        except Exception:
            return None
    return os.getenv(key.upper())


def test_ga4(db: Session) -> tuple[str, str]:
    try:
        property_id = _get_setting(db, 'ga4_property_id')
        if not property_id:
            return 'failed', 'GA4 property id is missing'
        if not property_id.isdigit():
            return 'failed', 'GA4 property id must be numeric'
        return 'connected', 'GA4 configuration looks valid'
    except Exception as exc:
        return 'failed', f'GA4 test error: {exc}'


def test_gsc(db: Session) -> tuple[str, str]:
    try:
        site_url = _get_setting(db, 'gsc_site_url')
        if not site_url:
            return 'failed', 'GSC site url is missing'
        if not (site_url.startswith('http://') or site_url.startswith('https://') or site_url.startswith('sc-domain:')):
            return 'failed', 'GSC site url must start with https:// or sc-domain:'
        return 'connected', 'GSC configuration looks valid'
    except Exception as exc:
        return 'failed', f'GSC test error: {exc}'


def test_dataforseo(db: Session) -> tuple[str, str]:
    try:
        login = _get_setting(db, 'dataforseo_login')
        password = _get_setting(db, 'dataforseo_password')
        if not login or not password:
            return 'failed', 'DataForSEO login/password are missing'
        if '@' not in login:
            return 'failed', 'DataForSEO login should be an email'
        return 'connected', 'DataForSEO credentials are present'
    except Exception:
        return 'failed', traceback.format_exc(limit=1)
