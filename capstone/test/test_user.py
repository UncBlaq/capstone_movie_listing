import os

from dotenv import load_dotenv

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient
from fastapi  import status

from capstone.database import Base, get_db
from capstone.main import app

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.parametrize("username, email, password", [("newuser1", "newuser1@example.com", "123")])
def test_signup(client, setup_database, username, email, password):
    response = client.post(
        "/user/signup",
        json={"username": username, "email": email, "password": password}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["username"] == username
    assert response.json()["movies"] == []


@pytest.mark.parametrize("username, email, password", [("newuser2", "newuser1@example.com", "123")])
def test_invalid_email_sign_up(client, setup_database, username, email, password):
    #First Sign up a user
    initial = client.post(
        "/user/signup",
        json={"username": username, "email": email, "password": password}
    )
    #Then Sign up another with similar email
    response = client.post(
        "/user/signup",
        json={"username": "unique", "email": email, "password": password}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.parametrize("username, email, password", [("newuser1", "newuser2@example.com", "123")])
def test_invalid_username_sign_up(client, setup_database, username, email, password):

    #First Sign up a user
    initial = client.post(
        "/user/signup",
        json={"username": username, "email": email, "password": password}
    )
    #Then Sign up another with similar username
    response = client.post(
        "/user/signup",
        json={"username": username, "email": "unique", "password": password}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.parametrize("username, email, password", [("newuser2", "newuser2@example.com", "123")])
def test_login(client, setup_database, username, email, password):
    # First, sign up the user
    response = client.post(
        "/user/signup",
        json={"username": username, "email": email, "password": password}
    )
    assert response.status_code == status.HTTP_201_CREATED
    # Then login the user
    response = client.post(
        "/user/auth/login",
        data = {"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"


@pytest.mark.parametrize("username, email, password", [("Invalid", "newuser999@example.com", "123")])
def test_invalid_user_login(client, setup_database, username, email, password):
    response = client.post(
        "/user/auth/login",
        data = {"username": username, "password": password}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Invalid credentials"}


@pytest.mark.parametrize("username, email, password", [("username", "email", "password")])
def test_password_incorrect(client, setup_database, username, email, password):
      # First, sign up the user
    response = client.post(
        "/user/signup",
        json={"username": username, "email": email, "password": password}
    )
    # Then, login the user with incorrect password
    response = client.post(
        "/user/auth/login",
        data = {username: username, password: "invalid"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect password"}



