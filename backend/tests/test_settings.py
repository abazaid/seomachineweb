from fastapi.testclient import TestClient

from tests.utils import register_and_login


def test_admin_can_save_settings(client: TestClient):
    token = register_and_login(client, role='admin')
    response = client.put(
        '/api/v1/settings',
        headers={'Authorization': f'Bearer {token}'},
        json={'ga4_property_id': '123456', 'gsc_site_url': 'https://zerovape.store'},
    )

    assert response.status_code == 200
    assert response.json()['ga4_property_id'] == '123456'


def test_non_admin_cannot_save_settings(client: TestClient):
    token = register_and_login(client, role='writer')
    response = client.put(
        '/api/v1/settings',
        headers={'Authorization': f'Bearer {token}'},
        json={'ga4_property_id': '123456'},
    )

    assert response.status_code == 403
