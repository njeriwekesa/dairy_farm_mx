import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.farms.models import Farm
from apps.cattle.models import Cattle
from apps.milking.models import MilkProduction
from apps.milking.services import (
    get_total_and_average,
    group_by_day,
    group_by_week,
    group_by_month,
)

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
        "/api/v1/milk/",
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
    user_cattle = Cattle.objects.create(
        farm=farm,
        tag_number="COW002",
        breed="Jersey",
        gender="female",
        date_of_birth="2022-01-01"
    )
    MilkProduction.objects.create(
        cattle=user_cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="8.0"
    )

    other_farm = Farm.objects.create(
        name="Other Farm",
        location="Kisumu",
        owner=other_user
    )
    other_cattle = Cattle.objects.create(
        farm=other_farm,
        tag_number="COW999",
        breed="Friesian",
        gender="female",
        date_of_birth="2021-01-01"
    )
    MilkProduction.objects.create(
        cattle=other_cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="20.0"
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/milk/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["cattle"] == user_cattle.id


@pytest.mark.django_db
def test_retrieve_milk_record(api_client, user, milk_record):
    api_client.force_authenticate(user=user)

    response = api_client.get(f"/api/v1/milk/{milk_record.id}/")

    assert response.status_code == 200
    assert response.data["id"] == milk_record.id


@pytest.mark.django_db
def test_update_milk_record(api_client, user, milk_record):
    api_client.force_authenticate(user=user)

    response = api_client.put(
        f"/api/v1/milk/{milk_record.id}/",
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
def test_cannot_change_cattle_on_update(api_client, user, milk_record):
    other_cattle = Cattle.objects.create(
        farm=milk_record.cattle.farm,
        tag_number="COW123",
        breed="Jersey",
        gender="female",
        date_of_birth="2022-01-01"
    )

    api_client.force_authenticate(user=user)
    response = api_client.put(
        f"/api/v1/milk/{milk_record.id}/",
        {
            "cattle": other_cattle.id,
            "date_time": milk_record.date_time,
            "liters": milk_record.liters
        },
        format="json"
    )

    assert response.status_code == 200
    assert response.data["cattle"] == milk_record.cattle.id


@pytest.mark.django_db
def test_delete_milk_record(api_client, user, milk_record):
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/v1/milk/{milk_record.id}/")

    assert response.status_code == 204
    assert MilkProduction.objects.count() == 0


# ----------------- Permissions -----------------
@pytest.mark.django_db
def test_other_user_cannot_access_record(api_client, other_user, milk_record):
    api_client.force_authenticate(user=other_user)

    response = api_client.get(f"/api/v1/milk/{milk_record.id}/")
    assert response.status_code == 404

    response = api_client.delete(f"/api/v1/milk/{milk_record.id}/")
    assert response.status_code == 404


# ----------------- Service Unit Tests -----------------
@pytest.mark.django_db
def test_get_total_and_average(cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T12:00:00Z",
        liters="20.0"
    )
    queryset = MilkProduction.objects.filter(cattle=cattle)
    result = get_total_and_average(queryset)

    assert result["total_liters"] == 30.0
    assert result["average_liters_per_record"] == 15.0


@pytest.mark.django_db
def test_group_by_day(cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T12:00:00Z",
        liters="20.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-27T08:00:00Z",
        liters="15.0"
    )
    queryset = MilkProduction.objects.filter(cattle=cattle)
    result = group_by_day(queryset)

    assert result["2026-02-26"] == 30.0
    assert result["2026-02-27"] == 15.0


@pytest.mark.django_db
def test_group_by_week(cattle):
    # both dates fall in the same week (Mon 2026-02-23)
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-27T08:00:00Z",
        liters="20.0"
    )
    queryset = MilkProduction.objects.filter(cattle=cattle)
    result = group_by_week(queryset)

    assert result["2026-02-23"] == 30.0


@pytest.mark.django_db
def test_group_by_month(cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-03-01T08:00:00Z",
        liters="20.0"
    )
    queryset = MilkProduction.objects.filter(cattle=cattle)
    result = group_by_month(queryset)

    assert result["2026-02"] == 10.0
    assert result["2026-03"] == 20.0


# ----------------- Summary Endpoint -----------------
@pytest.mark.django_db
def test_summary_endpoint_total(api_client, user, cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T12:00:00Z",
        liters="20.0"
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/milk/summary/")

    assert response.status_code == 200
    assert response.data["total_liters"] == 30.0
    assert response.data["average_liters_per_record"] == 15.0


@pytest.mark.django_db
def test_summary_endpoint_daily(api_client, user, cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-27T08:00:00Z",
        liters="20.0"
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/milk/summary/?period=daily")

    assert response.status_code == 200
    assert response.data["2026-02-26"] == 10.0
    assert response.data["2026-02-27"] == 20.0


@pytest.mark.django_db
def test_summary_endpoint_weekly(api_client, user, cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-27T08:00:00Z",
        liters="20.0"
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/milk/summary/?period=weekly")

    assert response.status_code == 200
    assert response.data["2026-02-23"] == 30.0


@pytest.mark.django_db
def test_summary_endpoint_monthly(api_client, user, cattle):
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cattle,
        date_time="2026-03-01T08:00:00Z",
        liters="20.0"
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/milk/summary/?period=monthly")

    assert response.status_code == 200
    assert response.data["2026-02"] == 10.0
    assert response.data["2026-03"] == 20.0


# ----------------- Filtering -----------------
@pytest.mark.django_db
def test_filter_by_cattle_tag_and_date(api_client, user, farm):
    cow1 = Cattle.objects.create(
        farm=farm,
        tag_number="COW001",
        breed="Friesian",
        gender="female",
        date_of_birth="2022-01-01"
    )
    cow2 = Cattle.objects.create(
        farm=farm,
        tag_number="COW002",
        breed="Jersey",
        gender="female",
        date_of_birth="2022-01-01"
    )

    MilkProduction.objects.create(
        cattle=cow1,
        date_time="2026-02-26T08:00:00Z",
        liters="10.0"
    )
    MilkProduction.objects.create(
        cattle=cow2,
        date_time="2026-02-26T08:00:00Z",
        liters="20.0"
    )

    api_client.force_authenticate(user=user)

    response = api_client.get("/api/v1/milk/?cattle__tag_number=COW001")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["cattle"] == cow1.id

    response = api_client.get(
        "/api/v1/milk/?start_date=2026-02-26T07:00:00Z&end_date=2026-02-26T09:00:00Z"
    )
    assert response.status_code == 200
    assert len(response.data) == 2