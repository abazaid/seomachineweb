from fastapi.testclient import TestClient

from tests.utils import register_and_login


class FakeAsyncResult:
    def delay(self, report_id: int):
        from app.workers import tasks

        tasks.run_performance_report(report_id)


def test_tasks_flow_from_report(client: TestClient, monkeypatch):
    token = register_and_login(client, role='admin')
    headers = {'Authorization': f'Bearer {token}'}

    monkeypatch.setattr('app.api.routers.reports.run_performance_report', FakeAsyncResult())

    report_resp = client.post('/api/v1/reports/performance-review', headers=headers, json={'days': 7})
    report_id = report_resp.json()['id']

    create_tasks_resp = client.post(f'/api/v1/tasks/from-report/{report_id}', headers=headers)
    assert create_tasks_resp.status_code == 200
    assert create_tasks_resp.json()['created_count'] >= 1

    tasks_resp = client.get('/api/v1/tasks', headers=headers)
    assert tasks_resp.status_code == 200
    task_id = tasks_resp.json()[0]['id']

    move_resp = client.patch(f'/api/v1/tasks/{task_id}/status', headers=headers, json={'status': 'done'})
    assert move_resp.status_code == 200
    assert move_resp.json()['status'] == 'done'
