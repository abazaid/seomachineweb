from fastapi.testclient import TestClient

from tests.utils import register_and_login


def test_login_and_me(client: TestClient):
    token = register_and_login(client, role='manager')

    response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json()['role'] == 'manager'
