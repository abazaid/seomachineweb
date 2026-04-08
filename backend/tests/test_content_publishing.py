from fastapi.testclient import TestClient

from tests.utils import register_and_login


class FakeAsyncResult:
    def delay(self, report_id: int):
        from app.workers import tasks

        tasks.run_performance_report(report_id)


def test_content_pipeline_and_publishing(client: TestClient, monkeypatch):
    token = register_and_login(client, role='admin')
    headers = {'Authorization': f'Bearer {token}'}

    brief_resp = client.post('/api/v1/content/brief', headers=headers, json={'keyword': '???', 'title': '???? ???'})
    assert brief_resp.status_code == 200
    content_id = brief_resp.json()['id']

    draft_resp = client.post(f'/api/v1/content/{content_id}/draft', headers=headers, json={'notes': 'draft'})
    assert draft_resp.status_code == 200
    assert draft_resp.json()['status'] == 'draft'

    optimize_resp = client.post(f'/api/v1/content/{content_id}/optimize', headers=headers, json={'notes': 'opt'})
    assert optimize_resp.status_code == 200
    assert optimize_resp.json()['status'] == 'optimized'

    publish_resp = client.post(f'/api/v1/publishing/publish/content/{content_id}', headers=headers)
    assert publish_resp.status_code == 200

    monkeypatch.setattr('app.api.routers.reports.run_performance_report', FakeAsyncResult())
    report_resp = client.post('/api/v1/reports/performance-review', headers=headers, json={'days': 7})
    report_id = report_resp.json()['id']

    export_resp = client.post(f'/api/v1/publishing/export/report/{report_id}?format=markdown', headers=headers)
    assert export_resp.status_code == 200
    assert export_resp.json()['format'] == 'markdown'

    logs_resp = client.get('/api/v1/publishing/audit-logs', headers=headers)
    assert logs_resp.status_code == 200
    assert len(logs_resp.json()) >= 2
