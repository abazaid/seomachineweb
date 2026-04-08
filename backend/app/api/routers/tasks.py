import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.report import Report
from app.models.task import Task
from app.models.user import User
from app.schemas.tasks import TaskCreateFromReportResponse, TaskOut, TaskStatusUpdateRequest
from app.services.report_service import dump_report_json, generate_performance_report


router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.post('/from-report/{report_id}', response_model=TaskCreateFromReportResponse)
def create_tasks_from_report(
    report_id: int,
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

    payload = json.loads(report.result_json)
    recommendations = payload.get('recommendations', [])
    if not recommendations:
        recommendations = [
            {'title': 'Review connector setup', 'action': 'Complete all credentials and re-run report'},
            {'title': 'Prioritize target keywords', 'action': 'Select top opportunities for this week'},
        ]

    created = 0
    for idx, rec in enumerate(recommendations):
        title = rec.get('title') or f'Recommendation {idx + 1}'
        action = rec.get('action') or 'Review recommendation and execute.'
        score = max(10, 100 - idx * 10)

        db.add(
            Task(
                title=title,
                description=action,
                status='todo',
                priority_score=score,
                source_type='report_recommendation',
                source_reference=str(report.id),
                created_by_user_id=current_user.id,
            )
        )
        created += 1

    db.commit()
    return TaskCreateFromReportResponse(created_count=created)


@router.get('', response_model=list[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return db.query(Task).order_by(Task.priority_score.desc(), Task.created_at.desc()).all()


@router.patch('/{task_id}/status', response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdateRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    if payload.status not in {'todo', 'in_progress', 'done'}:
        raise HTTPException(status_code=400, detail='Invalid status')

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task
