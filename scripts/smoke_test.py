import argparse
import json
import sys
import time

import httpx


def request(client: httpx.Client, method: str, path: str, token: str | None = None, json_body: dict | None = None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    response = client.request(method, path, headers=headers, json=json_body)
    if response.status_code >= 400:
        raise RuntimeError(f"{method} {path} failed ({response.status_code}): {response.text}")
    if response.text:
        return response.json()
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description='Smoke test for Zero Vape SEO Platform API')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000', help='Backend base URL (without /api/v1)')
    parser.add_argument('--email', default='admin@zerovape.com')
    parser.add_argument('--password', default='Admin@12345')
    args = parser.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=120.0) as client:
        health = request(client, 'GET', '/health')
        print('health:', health)

        login = request(
            client,
            'POST',
            '/api/v1/auth/login',
            json_body={'email': args.email, 'password': args.password},
        )
        token = login['access_token']
        print('login: ok')

        settings = request(
            client,
            'PUT',
            '/api/v1/settings',
            token=token,
            json_body={
                'ga4_property_id': '123456',
                'gsc_site_url': 'sc-domain:zerovape.store',
                'dataforseo_login': 'ops@example.com',
                'dataforseo_password': 'secret-pass',
                'ai_provider': 'openai',
                'ai_api_key': 'dummy-key',
            },
        )
        print('settings: saved', settings.get('ga4_property_id'))

        connections = request(client, 'POST', '/api/v1/connections/test', token=token)
        print('connections:', [f"{p['provider']}={p['status']}" for p in connections['providers']])

        report = request(
            client,
            'POST',
            '/api/v1/reports/performance-review',
            token=token,
            json_body={'days': 7},
        )
        report_id = report['id']
        print('report queued:', report_id)

        # Give async workers a short window if available.
        time.sleep(1)

        report_details = request(client, 'GET', f'/api/v1/reports/{report_id}', token=token)
        print('report status:', report_details['status'])

        task_gen = request(client, 'POST', f'/api/v1/tasks/from-report/{report_id}', token=token)
        print('tasks created:', task_gen['created_count'])

        tasks = request(client, 'GET', '/api/v1/tasks', token=token)
        if not tasks:
            raise RuntimeError('No tasks found after generation')
        task_id = tasks[0]['id']
        updated_task = request(
            client,
            'PATCH',
            f'/api/v1/tasks/{task_id}/status',
            token=token,
            json_body={'status': 'done'},
        )
        print('task moved:', updated_task['id'], updated_task['status'])

        brief = request(
            client,
            'POST',
            '/api/v1/content/brief',
            token=token,
            json_body={'keyword': '??? ???? ???????', 'title': '???? ??? ???? ???????'},
        )
        content_id = brief['id']
        print('content brief:', content_id)

        draft = request(
            client,
            'POST',
            f'/api/v1/content/{content_id}/draft',
            token=token,
            json_body={'notes': 'smoke test draft'},
        )
        optimize = request(
            client,
            'POST',
            f'/api/v1/content/{content_id}/optimize',
            token=token,
            json_body={'notes': 'smoke test optimize'},
        )
        publish = request(client, 'POST', f'/api/v1/publishing/publish/content/{content_id}', token=token)
        print('content stages:', draft['status'], optimize['status'], publish['status'])

        export_md = request(client, 'POST', f'/api/v1/publishing/export/report/{report_id}?format=markdown', token=token)
        export_csv = request(client, 'POST', f'/api/v1/publishing/export/report/{report_id}?format=csv', token=token)
        print('exports:', export_md['file_path'], export_csv['file_path'])

        logs = request(client, 'GET', '/api/v1/publishing/audit-logs', token=token)
        print('audit logs:', len(logs))

        summary = {
            'health': health,
            'report_id': report_id,
            'task_id': task_id,
            'content_id': content_id,
            'audit_logs': len(logs),
        }
        print('smoke test passed')
        print(json.dumps(summary, ensure_ascii=False))
        return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'smoke test failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
