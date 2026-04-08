from fastapi.testclient import TestClient

from tests.utils import register_and_login


def test_connection_tests_returns_statuses(client: TestClient):
    token = register_and_login(client, role='admin')

    client.put(
        '/api/v1/settings',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ga4_property_id': '123456',
            'gsc_site_url': 'sc-domain:zerovape.store',
            'dataforseo_login': 'ops@example.com',
            'dataforseo_password': 'secret-pass',
        },
    )

    response = client.post('/api/v1/connections/test', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload['providers']) == 3
    assert all(item['status'] == 'connected' for item in payload['providers'])
