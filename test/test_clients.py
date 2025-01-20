
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlmodel import SQLModel, Session
from app.core.database import get_session
from app.main import app
from app.models import Client


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

def test_create_client_success(test_client: TestClient):
    response = test_client.post("/api/clients", json={"name": "Fulano", "dni": "49370908M", "requested_capital": 10000})
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Fulano"
    assert data["dni"] == "49370908M"
    assert data["requested_capital"] == 10000


def test_create_client_fail(test_client: TestClient):
    response = test_client.post("/api/clients", json={"name": "Fulano", "dni": "49370918M", "requested_capital": 10000})
    assert response.status_code == 422

def test_read_client_success(session: Session, test_client: TestClient):
    client_1 = Client(name="Fulano", dni="49370908M", requested_capital=10000)
    session.add(client_1)
    session.commit()
    response = test_client.get("/api/clients/1")

    data = response.json()
    assert response.status_code == 200
    assert data == {'client': {'dni': '49370908M', 'requested_capital': 10000, 'id': 1, 'name': 'Fulano'}, 'mortgages': []}

def test_simulate_mortgage_success(session: Session, test_client: TestClient):
    client_1 = Client(name="Fulano", dni="49370908M", requested_capital=10000)
    session.add(client_1)
    session.commit()
    response = test_client.post("/api/clients/1/simulate-mortgage", json={"tae": 2.3, "installments": 4})
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data["monthly_payment"] == 218.26
    assert data["total"] == 10476.63

def test_simulate_mortgage_fail(session: Session, test_client: TestClient):
    response = test_client.post("/api/clients/1/simulate-mortgage", json={"tae": 2.3, "installments": 4})
    data = response.json()
    assert response.status_code == 404