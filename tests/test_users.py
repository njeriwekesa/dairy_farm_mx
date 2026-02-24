import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username="tester",
        email="tester@example.com",
        password="TestPass123"
    )

@pytest.fixture
def registered_user(api_client):
    response = api_client.post(
        "/api/users/register/",
        {
            "email": "farmer@example.com",
            "username": "farmer",
            "password": "StrongPass123",
            "farm_name": "My Dairy Farm"
        },
        format="json"
    )
    return response

@pytest.mark.django_db
def test_user_creation(user):
    assert user.email == "tester@example.com"

@pytest.mark.django_db
def test_registration_endpoint(registered_user):
    assert registered_user.status_code == 201
    assert registered_user.data["message"] == "Farm owner registered successfully"

@pytest.mark.django_db
def test_jwt_login_and_profile(user, api_client):
    # login
    login_response = api_client.post(
        "/api/token/",
        {"email": "tester@example.com", "password": "TestPass123"},
        format="json"
    )
    assert login_response.status_code == 200
    assert "access" in login_response.data
    assert "refresh" in login_response.data

    access_token = login_response.data["access"]

    # access profile
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    profile_response = api_client.get("/api/users/me/")
    assert profile_response.status_code == 200

    data = profile_response.data
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["username"] == user.username
    assert data["role"] == user.role

    # farms list
    assert isinstance(data["farms"], list)
    # optional: if user has one farm, check its structure
    if data["farms"]:
        farm = data["farms"][0]
        assert "id" in farm
        assert "name" in farm
        assert "location" in farm


@pytest.mark.django_db
def test_token_refresh(user, api_client):

    login_response = api_client.post(
        "/api/token/",
        {"email": "tester@example.com", "password": "TestPass123"},
        format="json"
    )
    refresh_token = login_response.data["refresh"]

    # refresh access token
    refresh_response = api_client.post(
        "/api/token/refresh/",
        {"refresh": refresh_token},
        format="json"
    )
    assert refresh_response.status_code == 200
    assert "access" in refresh_response.data