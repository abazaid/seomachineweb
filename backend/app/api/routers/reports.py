from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.report import Report
from app.models.user import User
from app.schemas.reports import ReportCreateRequest, ReportDetailResponse, ReportResponse
from app.workers.tasks import run_performance_report


router = APIRouter(prefix='/reports', tags=['reports'])


@router.post('/performance-review', response_model=ReportResponse, status_code=status.HTTP_202_ACCEPTED)
def create_performance_report_job(
    payload: ReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = Report(
        report_type='performance_review',
        status='queued',
        days=payload.days,
        created_by_user_id=current_user.id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    try:
        run_performance_report.delay(report.id)
    except Exception:
        # Local fallback when broker/worker are unavailable.
        run_performance_report(report.id)
    return report


@router.get('', response_model=list[ReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return db.query(Report).order_by(Report.created_at.desc()).all()


@router.get('/{report_id}', response_model=ReportDetailResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')
    return report
