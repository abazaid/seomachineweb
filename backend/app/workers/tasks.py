from app.core.db import SessionLocal
from app.models.report import Report
from app.services.report_service import dump_report_json, generate_performance_report, report_to_markdown
from app.workers.celery_app import celery_app


@celery_app.task(name='run_performance_report')
def run_performance_report(report_id: int) -> None:
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return

        report.status = 'running'
        db.commit()

        data = generate_performance_report(days=report.days)
        markdown_path = report_to_markdown(report.id, data)

        report.status = 'done'
        report.result_json = dump_report_json(data)
        report.markdown_path = markdown_path
        db.commit()
    except Exception as exc:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = 'failed'
            report.error_message = str(exc)
            db.commit()
    finally:
        db.close()
