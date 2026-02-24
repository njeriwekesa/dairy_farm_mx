import pytest
from rest_framework.test import APIClient
from apps.users.models import CustomUser
from apps.farms.models import Farm

@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email="farmer2@example.com",
        username="farmer2",
        password="StrongPass123"
    )

@pytest.fixture
def auth_client(user):
    client = APIClient()
    # Obtain JWT token for the user
    response = client.post("/api/token/", {
        "email": user.email,
        "password": "StrongPass123"
    }, format="json")
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client

@pytest.mark.django_db
def test_create_farm(auth_client):
    data = {
        "name": "Sunny Farm",
        "location": "Nakuru",
        "description": "Test dairy farm"
    }
    response = auth_client.post("/api/farms/", data, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "Sunny Farm"
    assert Farm.objects.filter(owner__email="farmer2@example.com").exists()

@pytest.mark.django_db
def test_prevent_multiple_farms(auth_client):
    # First farm
    Farm.objects.create(owner=CustomUser.objects.get(email="farmer2@example.com"), name="Existing Farm")
    # Attempt second farm
    data = {"name": "Another Farm"}
    response = auth_client.post("/api/farms/", data, format="json")
    assert response.status_code == 400
    assert "already have a registered farm" in str(response.data)

@pytest.mark.django_db
def test_list_user_farm(auth_client):
    user = CustomUser.objects.get(email="farmer2@example.com")
    Farm.objects.create(owner=user, name="User Farm")
    
    response = auth_client.get("/api/farms/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "User Farm"
