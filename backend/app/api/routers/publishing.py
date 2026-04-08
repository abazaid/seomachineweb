from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.audit import AuditLog
from app.models.content import ContentItem
from app.models.report import Report
from app.models.user import User
from app.schemas.audit import AuditLogOut
from app.services.publishing_service import export_report_to_csv, export_report_to_markdown
from app.services.report_service import dump_report_json, generate_performance_report


router = APIRouter(prefix='/publishing', tags=['publishing'])


@router.post('/export/report/{report_id}')
def export_report(
    report_id: int,
    format: str = Query(default='markdown'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail='Report not found')

    if not report.result_json:
        data = generate_performance_report(days=report.days)
        report.result_json = dump_report_json(data)
        report.status = 'done'
        db.commit()
        db.refresh(report)

    if format == 'markdown':
        file_path = export_report_to_markdown(report.id, report.result_json)
    elif format == 'csv':
        file_path = export_report_to_csv(report.id, report.result_json)
    else:
        raise HTTPException(status_code=400, detail='Supported formats: markdown, csv')

    db.add(
        AuditLog(
            action='export_report',
            entity_type='report',
            entity_id=str(report.id),
            actor_user_id=current_user.id,
            details=f'format={format}, path={file_path}',
        )
    )
    db.commit()

    return {'file_path': file_path, 'format': format}


@router.post('/publish/content/{content_id}')
def publish_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Content item not found')

    item.status = 'published'

    db.add(
        AuditLog(
            action='publish_content',
            entity_type='content',
            entity_id=str(item.id),
            actor_user_id=current_user.id,
            details='Published via internal publish endpoint',
        )
    )
    db.commit()
    db.refresh(item)

    return {'status': 'published', 'content_id': item.id}


@router.get('/audit-logs', response_model=list[AuditLogOut])
def list_audit_logs(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
