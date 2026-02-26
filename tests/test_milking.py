import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.farms.models import Farm
from apps.cattle.models import Cattle
from apps.milking.models import MilkProduction

User = get_user_model()


# ----------------- Fixtures -----------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="user@example.com",
        password="TestPass123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="OtherPass123"
    )


@pytest.fixture
def farm(user, db):
    return Farm.objects.create(
        name="Test Farm",
        location="Nairobi",
        owner=user
    )


@pytest.fixture
def cattle(farm, db):
    return Cattle.objects.create(
        farm=farm,
        tag_number="COW001",
        breed="Friesian",
        gender="female",
        date_of_birth="2022-01-01"
    )


@pytest.fixture
def milk_record(cattle, db):
    return MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="12.50"
    )


# ----------------- CRUD Tests -----------------
@pytest.mark.django_db
def test_create_milk_record(api_client, user, cattle):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/milk/",
        {
            "cattle": cattle.id,
            "date_time": "2026-02-26T09:00:00Z",
            "liters": "10.00"
        },
        format="json"
    )

    assert response.status_code == 201
    assert MilkProduction.objects.count() == 1
    assert MilkProduction.objects.first().cattle == cattle


@pytest.mark.django_db
def test_list_only_user_records(api_client, user, other_user, farm):
    # user cattle
    user_cattle = Cattle.objects.create(
        farm=farm,
        tag_number="COW002",
        breed="Jersey",
        gender="female",
        date_of_birth="2022-01-01"
    )
    MilkProduction.objects.create(cattle=user_cattle, date_time="2026-02-26T08:00:00Z", liters="8.0")

    # other user cattle
    other_farm = Farm.objects.create(name="Other Farm", location="Kisumu", owner=other_user)
    other_cattle = Cattle.objects.create(farm=other_farm, tag_number="COW999", breed="Friesian", gender="female", date_of_birth="2021-01-01")
    MilkProduction.objects.create(cattle=other_cattle, date_time="2026-02-26T08:00:00Z", liters="20.0")

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/milk/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["cattle"] == user_cattle.id


@pytest.mark.django_db
def test_retrieve_milk_record(api_client, user, milk_record):
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/milk/{milk_record.id}/")

    assert response.status_code == 200
    assert response.data["id"] == milk_record.id


@pytest.mark.django_db
def test_update_milk_record(api_client, user, milk_record):
    api_client.force_authenticate(user=user)

    response = api_client.put(
        f"/api/milk/{milk_record.id}/",
        {
            "cattle": milk_record.cattle.id,
            "date_time": milk_record.date_time,
            "liters": "15.00"
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["liters"] == "15.00"


@pytest.mark.django_db
def test_cannot_change_cattle_on_update(api_client, user, other_user, milk_record):
    # create another cattle
    other_farm = Farm.objects.create(name="Other Farm", location="Kisumu", owner=user)
    other_cattle = Cattle.objects.create(farm=other_farm, tag_number="COW123", breed="Friesian", gender="female", date_of_birth="2022-01-01")

    api_client.force_authenticate(user=user)
    response = api_client.put(
        f"/api/milk/{milk_record.id}/",
        {
            "cattle": other_cattle.id,
            "date_time": milk_record.date_time,
            "liters": milk_record.liters
        },
        format="json"
    )

    assert response.status_code == 200
    # cattle should not have changed
    assert response.data["cattle"] == milk_record.cattle.id


@pytest.mark.django_db
def test_delete_milk_record(api_client, user, milk_record):
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/milk/{milk_record.id}/")

    assert response.status_code == 204
    assert MilkProduction.objects.count() == 0


# ----------------- Permissions -----------------
@pytest.mark.django_db
def test_other_user_cannot_access_record(api_client, other_user, milk_record):
    api_client.force_authenticate(user=other_user)

    # GET
    response = api_client.get(f"/api/milk/{milk_record.id}/")
    assert response.status_code == 404

    # DELETE
    response = api_client.delete(f"/api/milk/{milk_record.id}/")
    assert response.status_code == 404


# ----------------- Aggregation -----------------
@pytest.mark.django_db
def test_summary_endpoint(api_client, user, cattle):
    # create multiple milk records
    MilkProduction.objects.create(cattle=cattle, date_time="2026-02-26T08:00:00Z", liters="10.0")
    MilkProduction.objects.create(cattle=cattle, date_time="2026-02-26T12:00:00Z", liters="20.0")

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/milk/summary/")

    assert response.status_code == 200
    assert response.data["total_liters"] == 30.0
    assert response.data["average_liters_per_record"] == 15.0