from fastapi.testclient import TestClient


def register_and_login(client: TestClient, role: str = 'admin') -> str:
    client.post(
        '/api/v1/auth/register',
        json={
            'email': f'{role}@example.com',
            'full_name': f'{role} user',
            'password': 'Password123!',
            'role': role,
        },
    )
    response = client.post('/api/v1/auth/login', json={'email': f'{role}@example.com', 'password': 'Password123!'})
    return response.json()['access_token']
