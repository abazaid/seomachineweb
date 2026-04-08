import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
os.environ['JWT_SECRET'] = 'test-secret'
os.environ['SETTINGS_ENCRYPTION_KEY'] = 'test-encryption-key'

from app.core.db import Base, get_db
from app.main import app


SQLALCHEMY_TEST_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope='session', autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


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
