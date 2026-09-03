import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


def test_create_and_list_spaces():
    res = client.post("/spaces/", json={"name": "Meeting Room Alpha", "space_type": "meeting_room", "capacity": 6})
    assert res.status_code == 201
    assert res.json()["name"] == "Meeting Room Alpha"

    res_list = client.get("/spaces/")
    assert len(res_list.json()) == 1


def test_booking_conflict_prevention():
    space = client.post("/spaces/", json={"name": "Desk 101", "space_type": "hot_desk", "capacity": 1}).json()

    # Initial booking: 10:00 to 12:00
    booking1 = client.post(
        "/bookings/",
        json={
            "space_id": space["id"],
            "user_email": "user1@example.com",
            "start_time": "2026-10-01T10:00:00",
            "end_time": "2026-10-01T12:00:00",
        },
    )
    assert booking1.status_code == 201

    # Overlapping booking: 11:00 to 13:00 -> Expect 409 Conflict
    booking2 = client.post(
        "/bookings/",
        json={
            "space_id": space["id"],
            "user_email": "user2@example.com",
            "start_time": "2026-10-01T11:00:00",
            "end_time": "2026-10-01T13:00:00",
        },
    )
    assert booking2.status_code == 409
