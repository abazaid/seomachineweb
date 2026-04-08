from fastapi.testclient import TestClient

from app.workers import tasks
from tests.utils import register_and_login


class FakeAsyncResult:
    def delay(self, report_id: int):
        tasks.run_performance_report(report_id)


def test_create_and_fetch_report(client: TestClient, monkeypatch):
    token = register_and_login(client, role='admin')

    monkeypatch.setattr('app.api.routers.reports.run_performance_report', FakeAsyncResult())

    create_resp = client.post(
        '/api/v1/reports/performance-review',
        headers={'Authorization': f'Bearer {token}'},
        json={'days': 15},
    )

    assert create_resp.status_code == 202
    report_id = create_resp.json()['id']

    detail_resp = client.get(f'/api/v1/reports/{report_id}', headers={'Authorization': f'Bearer {token}'})
    assert detail_resp.status_code == 200
    assert detail_resp.json()['status'] in {'done', 'running', 'queued'}
