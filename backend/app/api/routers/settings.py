from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.db import get_db
from app.models.setting import SystemSetting
from app.models.user import User
from app.schemas.settings import SettingsResponse, SettingsUpsertRequest
from app.services.settings_service import decrypt_value, encrypt_value, mask_value


router = APIRouter(prefix='/settings', tags=['settings'])

_SETTING_KEYS = [
    'ga4_property_id',
    'gsc_site_url',
    'dataforseo_login',
    'dataforseo_password',
    'ai_provider',
    'ai_api_key',
]


def _settings_map(db: Session) -> dict[str, str]:
    rows = db.query(SystemSetting).all()
    data: dict[str, str] = {}
    for row in rows:
        data[row.key] = decrypt_value(row.value_encrypted)
    return data


@router.get('', response_model=SettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    data = _settings_map(db)
    return SettingsResponse(
        ga4_property_id=data.get('ga4_property_id'),
        gsc_site_url=data.get('gsc_site_url'),
        dataforseo_login_masked=mask_value(data.get('dataforseo_login')),
        dataforseo_password_masked=mask_value(data.get('dataforseo_password')),
        ai_provider=data.get('ai_provider'),
        ai_api_key_masked=mask_value(data.get('ai_api_key')),
    )


@router.put('', response_model=SettingsResponse)
def upsert_settings(
    payload: SettingsUpsertRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    incoming = payload.model_dump(exclude_none=True)

    for key in _SETTING_KEYS:
        if key not in incoming:
            continue

        value = incoming[key]
        existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        encrypted = encrypt_value(str(value))

        if existing:
            existing.value_encrypted = encrypted
            existing.updated_by_user_id = admin_user.id
        else:
            db.add(
                SystemSetting(
                    key=key,
                    value_encrypted=encrypted,
                    updated_by_user_id=admin_user.id,
                )
            )

    db.commit()
    return get_settings(db=db, _admin=admin_user)
