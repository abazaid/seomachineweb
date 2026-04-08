from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.connections import ConnectionTestResponse, ProviderStatus
from app.services.connections_service import test_dataforseo, test_ga4, test_gsc


router = APIRouter(prefix='/connections', tags=['connections'])


@router.post('/test', response_model=ConnectionTestResponse)
def run_connection_tests(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    ga4_status, ga4_msg = test_ga4(db)
    gsc_status, gsc_msg = test_gsc(db)
    dfs_status, dfs_msg = test_dataforseo(db)

    return ConnectionTestResponse(
        providers=[
            ProviderStatus(provider='ga4', status=ga4_status, message=ga4_msg),
            ProviderStatus(provider='gsc', status=gsc_status, message=gsc_msg),
            ProviderStatus(provider='dataforseo', status=dfs_status, message=dfs_msg),
        ]
    )
