import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.farms.models import Farm
from apps.sales.models import Buyer, Sale

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="salesuser",
        email="sales@example.com",
        password="TestPass123",
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="OtherPass123",
    )


@pytest.fixture
def farm(user, db):
    return Farm.objects.create(
        name="Sales Farm",
        location="Nairobi",
        owner=user,
    )


@pytest.fixture
def buyer(farm, db):
    return Buyer.objects.create(
        farm=farm,
        name="Retail Buyer",
        buyer_type="walk_in",
        contact="0700000000",
    )


@pytest.fixture
def sale(farm, buyer, db):
    return Sale.objects.create(
        farm=farm,
        buyer=buyer,
        liters_sold="20.00",
        price_per_litre="50.00",
        total_amount="1000.00",
        date="2026-04-01",
        notes="Fixture sale",
    )


@pytest.mark.django_db
def test_create_buyer_success(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/buyers/",
        {
            "farm": farm.id,
            "name": "Hotel Buyer",
            "buyer_type": "b2b",
            "contact": "0712345678",
            "notes": "Regular customer",
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Buyer.objects.count() == 1
    created = Buyer.objects.first()
    assert created.name == "Hotel Buyer"
    assert created.farm == farm


@pytest.mark.django_db
def test_duplicate_buyer_name_same_farm_returns_400(api_client, user, farm):
    Buyer.objects.create(
        farm=farm,
        name="Duplicate Buyer",
        buyer_type="walk_in",
    )

    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/v1/buyers/",
        {
            "farm": farm.id,
            "name": "Duplicate Buyer",
            "buyer_type": "b2b",
            "is_active": True,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_sale_success_total_amount_computed(api_client, user, farm, buyer):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/sales/",
        {
            "farm": farm.id,
            "buyer": buyer.id,
            "liters_sold": "10.50",
            "price_per_litre": "42.00",
            "total_amount": "0.00",
            "date": "2026-04-02",
            "notes": "Morning sale",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Sale.objects.count() == 1
    created = Sale.objects.first()
    assert str(created.total_amount) == "441.00"
    assert response.data["total_amount"] == "441.00"


@pytest.mark.django_db
def test_list_sales_returns_only_authenticated_users_records(
    api_client, user, other_user, farm, buyer
):
    Sale.objects.create(
        farm=farm,
        buyer=buyer,
        liters_sold="5.00",
        price_per_litre="40.00",
        total_amount="200.00",
        date="2026-04-01",
    )

    other_farm = Farm.objects.create(
        name="Other Farm",
        location="Kisumu",
        owner=other_user,
    )
    other_buyer = Buyer.objects.create(
        farm=other_farm,
        name="Other Buyer",
        buyer_type="b2b",
    )
    Sale.objects.create(
        farm=other_farm,
        buyer=other_buyer,
        liters_sold="8.00",
        price_per_litre="45.00",
        total_amount="360.00",
        date="2026-04-01",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/sales/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["buyer"] == buyer.id


@pytest.mark.django_db
def test_other_user_cannot_access_sales_returns_404(api_client, other_user, sale):
    api_client.force_authenticate(user=other_user)

    response = api_client.get(f"/api/v1/sales/{sale.id}/")
    assert response.status_code == 404

    response = api_client.delete(f"/api/v1/sales/{sale.id}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_buyer_with_sales_history_returns_405(api_client, user, buyer, sale):
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/v1/buyers/{buyer.id}/")

    assert response.status_code == 405
    assert (
        response.data["detail"]
        == "Buyers cannot be deleted. Set is_active=False to deactivate."
    )


@pytest.mark.django_db
def test_delete_buyer_with_no_sales_history_returns_405(api_client, user, buyer):
    api_client.force_authenticate(user=user)

    response = api_client.delete(f"/api/v1/buyers/{buyer.id}/")

    assert response.status_code == 405
    assert (
        response.data["detail"]
        == "Buyers cannot be deleted. Set is_active=False to deactivate."
    )


@pytest.mark.django_db
def test_summary_endpoint_returns_totals_and_by_buyer(api_client, user, farm):
    buyer_a = Buyer.objects.create(
        farm=farm,
        name="Buyer A",
        buyer_type="walk_in",
    )
    buyer_b = Buyer.objects.create(
        farm=farm,
        name="Buyer B",
        buyer_type="b2b",
    )

    Sale.objects.create(
        farm=farm,
        buyer=buyer_a,
        liters_sold="10.00",
        price_per_litre="40.00",
        total_amount="400.00",
        date="2026-04-01",
    )
    Sale.objects.create(
        farm=farm,
        buyer=buyer_a,
        liters_sold="5.00",
        price_per_litre="44.00",
        total_amount="220.00",
        date="2026-04-02",
    )
    Sale.objects.create(
        farm=farm,
        buyer=buyer_b,
        liters_sold="8.00",
        price_per_litre="50.00",
        total_amount="400.00",
        date="2026-04-02",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/sales/summary/")

    assert response.status_code == 200
    assert response.data["total_sales"] == 3
    assert response.data["total_revenue"] == 1020
    assert response.data["total_liters_sold"] == 23
    assert len(response.data["by_buyer"]) == 2

    by_buyer = {item["buyer_name"]: item for item in response.data["by_buyer"]}
    assert by_buyer["Buyer A"]["buyer_type"] == "walk_in"
    assert by_buyer["Buyer A"]["sales_count"] == 2
    assert by_buyer["Buyer A"]["total_liters"] == 15
    assert by_buyer["Buyer A"]["total_revenue"] == 620
    assert by_buyer["Buyer B"]["buyer_type"] == "b2b"
    assert by_buyer["Buyer B"]["sales_count"] == 1
    assert by_buyer["Buyer B"]["total_liters"] == 8
    assert by_buyer["Buyer B"]["total_revenue"] == 400


@pytest.mark.django_db
def test_filter_by_start_date_end_date(api_client, user, farm, buyer):
    Sale.objects.create(
        farm=farm,
        buyer=buyer,
        liters_sold="6.00",
        price_per_litre="40.00",
        total_amount="240.00",
        date="2026-04-01",
    )
    Sale.objects.create(
        farm=farm,
        buyer=buyer,
        liters_sold="7.00",
        price_per_litre="40.00",
        total_amount="280.00",
        date="2026-04-10",
    )
    Sale.objects.create(
        farm=farm,
        buyer=buyer,
        liters_sold="8.00",
        price_per_litre="40.00",
        total_amount="320.00",
        date="2026-04-20",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get(
        "/api/v1/sales/?start_date=2026-04-05&end_date=2026-04-15"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["date"] == "2026-04-10"


@pytest.mark.django_db
def test_filter_by_buyer_type(api_client, user, farm):
    walk_in_buyer = Buyer.objects.create(
        farm=farm,
        name="Walk In Buyer",
        buyer_type="walk_in",
    )
    b2b_buyer = Buyer.objects.create(
        farm=farm,
        name="B2B Buyer",
        buyer_type="b2b",
    )

    Sale.objects.create(
        farm=farm,
        buyer=walk_in_buyer,
        liters_sold="5.00",
        price_per_litre="40.00",
        total_amount="200.00",
        date="2026-04-01",
    )
    Sale.objects.create(
        farm=farm,
        buyer=b2b_buyer,
        liters_sold="9.00",
        price_per_litre="50.00",
        total_amount="450.00",
        date="2026-04-01",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/sales/?buyer__buyer_type=b2b")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["buyer"] == b2b_buyer.id
