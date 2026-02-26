import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.farms.models import Farm
from apps.cattle.models import Cattle

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="owner@example.com",
        password="TestPass123",
        username="owner",
        role="owner"
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="other@example.com",
        password="TestPass123",
        username="other",
        role="owner"
    )


@pytest.fixture
def farm(user):
    return Farm.objects.create(
        name="Owner Farm",
        location="Nairobi",
        owner=user
    )


@pytest.fixture
def cattle(farm):
    return Cattle.objects.create(
        farm=farm,
        tag_number="TAG001",
        breed="Friesian",
        gender="female",
        date_of_birth="2022-01-01"
    )

@pytest.mark.django_db
def test_owner_can_create_cattle(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cattle/",
        {
            "farm": farm.id,
            "tag_number": "TAG002",
            "breed": "Jersey",
            "gender": "female",
            "date_of_birth": "2023-01-01"
        },
        format="json"
    )

    assert response.status_code == 201
    assert Cattle.objects.count() == 1
    assert Cattle.objects.first().farm.owner == user

@pytest.mark.django_db
def test_cannot_create_cattle_for_other_users_farm(
    api_client, user, another_user
):
    other_farm = Farm.objects.create(
        name="Other Farm",
        location="Kisumu",
        owner=another_user
    )

    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/cattle/",
        {
            "farm": other_farm.id,
            "tag_number": "TAG003",
            "breed": "Jersey",
            "gender": "female",
            "date_of_birth": "2023-01-01"
        },
        format="json"
    )

    assert response.status_code == 403
    assert Cattle.objects.count() == 0

@pytest.mark.django_db
def test_list_returns_only_owned_cattle(
    api_client, user, another_user, farm
):
    # Owner cattle
    Cattle.objects.create(
        farm=farm,
        tag_number="TAG001",
        breed="Friesian",
        gender="female",
        date_of_birth="2022-01-01"
    )

    # Other user's farm + cattle
    other_farm = Farm.objects.create(
        name="Other Farm",
        location="Kisumu",
        owner=another_user
    )

    Cattle.objects.create(
        farm=other_farm,
        tag_number="TAG999",
        breed="Jersey",
        gender="female",
        date_of_birth="2021-01-01"
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/cattle/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["tag_number"] == "TAG001"

@pytest.mark.django_db
def test_filtering_by_breed(api_client, user, farm):
    Cattle.objects.create(
        farm=farm,
        tag_number="TAG001",
        breed="Friesian",
        gender="female",
        date_of_birth="2022-01-01"
    )

    Cattle.objects.create(
        farm=farm,
        tag_number="TAG002",
        breed="Jersey",
        gender="female",
        date_of_birth="2022-01-01"
    )

    api_client.force_authenticate(user=user)

    response = api_client.get("/api/cattle/?breed=Friesian")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["breed"] == "Friesian"

@pytest.mark.django_db
def test_owner_can_retrieve_cattle(api_client, user, cattle):
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/cattle/{cattle.id}/")

    assert response.status_code == 200
    assert response.data["id"] == cattle.id

@pytest.mark.django_db
def test_other_user_cannot_retrieve_cattle(
    api_client, another_user, cattle
):
    api_client.force_authenticate(user=another_user)

    response = api_client.get(f"/api/cattle/{cattle.id}/")

    assert response.status_code == 404

@pytest.mark.django_db
def test_owner_can_update_cattle(api_client, user, cattle):
    api_client.force_authenticate(user=user)

    response = api_client.put(
        f"/api/cattle/{cattle.id}/",
        {
            "farm": cattle.farm.id,
            "tag_number": "TAG001",
            "breed": "Jersey",
            "gender": "female",
            "date_of_birth": "2022-01-01"
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["breed"] == "Jersey"

@pytest.mark.django_db
def test_cannot_change_farm_on_update(
    api_client, user, another_user, cattle
):
    new_farm = Farm.objects.create(
        name="New Farm",
        location="Mombasa",
        owner=user
    )

    api_client.force_authenticate(user=user)

    response = api_client.put(
        f"/api/cattle/{cattle.id}/",
        {
            "farm": new_farm.id,
            "tag_number": cattle.tag_number,
            "breed": cattle.breed,
            "gender": cattle.gender,
            "date_of_birth": cattle.date_of_birth
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["farm"] == cattle.farm.id

@pytest.mark.django_db
def test_owner_can_delete_cattle(api_client, user, cattle):
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/cattle/{cattle.id}/")

    assert response.status_code == 204
    assert Cattle.objects.count() == 0

@pytest.mark.django_db
def test_other_user_cannot_delete_cattle(
    api_client, another_user, cattle
):
    api_client.force_authenticate(user=another_user)

    response = api_client.delete(f"/api/cattle/{cattle.id}/")

    assert response.status_code == 404                    

