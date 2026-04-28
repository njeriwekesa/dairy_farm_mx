import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.farms.models import Farm
from apps.expenses.models import (
    Supplier,
    InventoryItem,
    InventoryPurchase,
    InventoryUsage,
    Expense,
)
from apps.expenses import services

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="expenseuser",
        email="expense@example.com",
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
        name="Main Farm",
        location="Nairobi",
        owner=user,
    )


@pytest.fixture
def other_farm(other_user, db):
    return Farm.objects.create(
        name="Other Farm",
        location="Kisumu",
        owner=other_user,
    )


@pytest.fixture
def supplier(farm, db):
    return Supplier.objects.create(
        farm=farm,
        name="Local Supplier",
        supplier_type="walk_in",
        is_active=True,
    )


@pytest.fixture
def inventory_item(farm, db):
    return InventoryItem.objects.create(
        farm=farm,
        name="Dairy Meal",
        item_type="feed",
        unit="kg",
        quantity_on_hand=Decimal("100.00"),
        reorder_threshold=Decimal("20.00"),
        is_active=True,
    )


# ----------------- Supplier Tests -----------------
@pytest.mark.django_db
def test_create_supplier_success(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/suppliers/",
        {
            "name": "AgroVet Ltd",
            "supplier_type": "walk_in",
        },
        format="json",
    )

    assert response.status_code == 201
    assert Supplier.objects.filter(name="AgroVet Ltd").exists()
    created = Supplier.objects.get(name="AgroVet Ltd")
    assert created.farm.owner == user


@pytest.mark.django_db
def test_duplicate_supplier_name_same_farm_returns_400(api_client, user, supplier):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/suppliers/",
        {
            "name": supplier.name,
            "supplier_type": supplier.supplier_type,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_delete_supplier_returns_405(api_client, user, farm):
    api_client.force_authenticate(user=user)
    create_response = api_client.post(
        "/api/v1/suppliers/",
        {
            "name": "Delete Block Supplier",
            "supplier_type": "walk_in",
        },
        format="json",
    )
    supplier_id = create_response.data["id"]

    response = api_client.delete(f"/api/v1/suppliers/{supplier_id}/")

    assert response.status_code == 405
    assert "deactivate" in str(response.data).lower()


@pytest.mark.django_db
def test_other_user_cannot_access_supplier(api_client, other_user, supplier):
    api_client.force_authenticate(user=other_user)

    response = api_client.get(f"/api/v1/suppliers/{supplier.id}/")

    assert response.status_code == 404


# ----------------- InventoryItem Tests -----------------
@pytest.mark.django_db
def test_create_inventory_item_success(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/inventory/",
        {
            "name": "Mineral Mix",
            "item_type": "supplement",
            "unit": "kg",
            "reorder_threshold": "10.00",
        },
        format="json",
    )

    assert response.status_code == 201
    created = InventoryItem.objects.get(name="Mineral Mix")
    assert created.quantity_on_hand == Decimal("0.00")
    assert created.farm.owner == user


@pytest.mark.django_db
def test_quantity_on_hand_is_read_only(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/inventory/",
        {
            "name": "Silage",
            "item_type": "feed",
            "unit": "kg",
            "quantity_on_hand": "999.00",
            "reorder_threshold": "50.00",
        },
        format="json",
    )

    assert response.status_code == 201
    created = InventoryItem.objects.get(name="Silage")
    assert created.quantity_on_hand == Decimal("0.00")


@pytest.mark.django_db
def test_other_user_cannot_access_inventory_item(api_client, other_user, inventory_item):
    api_client.force_authenticate(user=other_user)

    response = api_client.get(f"/api/v1/inventory/{inventory_item.id}/")

    assert response.status_code == 404


# ----------------- InventoryPurchase Tests -----------------
@pytest.mark.django_db
def test_record_inventory_purchase_success(api_client, user, inventory_item):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/inventory-purchases/",
        {
            "inventory_item": inventory_item.id,
            "quantity": "50.00",
            "unit_cost": "10.00",
            "date": "2026-04-20",
        },
        format="json",
    )

    assert response.status_code == 201
    inventory_item.refresh_from_db()
    assert inventory_item.quantity_on_hand == Decimal("150.00")

    purchase = InventoryPurchase.objects.get(id=response.data["id"])
    expense = Expense.objects.get(inventory_purchase=purchase)
    assert expense.category == inventory_item.item_type
    assert expense.amount == Decimal("500.00")


@pytest.mark.django_db
def test_inventory_purchase_expense_category_derived_from_item_type(
    api_client, user, farm
):
    item = InventoryItem.objects.create(
        farm=farm,
        name="Mineral Supplement",
        item_type="supplement",
        unit="kg",
        quantity_on_hand=Decimal("20.00"),
        reorder_threshold=Decimal("5.00"),
        is_active=True,
    )

    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/v1/inventory-purchases/",
        {
            "inventory_item": item.id,
            "quantity": "10.00",
            "unit_cost": "8.00",
            "date": "2026-04-21",
        },
        format="json",
    )

    assert response.status_code == 201
    purchase = InventoryPurchase.objects.get(id=response.data["id"])
    expense = Expense.objects.get(inventory_purchase=purchase)
    assert expense.category == "supplement"


# ----------------- InventoryUsage Tests -----------------
@pytest.mark.django_db
def test_record_inventory_usage_success(api_client, user, inventory_item):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/inventory-usage/",
        {
            "inventory_item": inventory_item.id,
            "quantity_used": "30.00",
            "date": "2026-04-21",
        },
        format="json",
    )

    assert response.status_code == 201
    inventory_item.refresh_from_db()
    assert inventory_item.quantity_on_hand == Decimal("70.00")


@pytest.mark.django_db
def test_record_inventory_usage_exceeds_stock_returns_400(
    api_client, user, inventory_item
):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/inventory-usage/",
        {
            "inventory_item": inventory_item.id,
            "quantity_used": "150.00",
            "date": "2026-04-21",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "stock" in str(response.data).lower()


# ----------------- Expense Tests -----------------
@pytest.mark.django_db
def test_create_pure_expense_success(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/expenses/",
        {
            "category": "vet",
            "amount": "300.00",
            "date": "2026-04-22",
            "notes": "Vet visit",
        },
        format="json",
    )

    assert response.status_code == 201
    expense = Expense.objects.get(id=response.data["id"])
    assert expense.farm.owner == user
    assert expense.supplier is None
    assert expense.inventory_item is None


@pytest.mark.django_db
def test_create_expense_with_supplier_success(api_client, user, supplier):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/expenses/",
        {
            "category": "labor",
            "amount": "500.00",
            "date": "2026-04-22",
            "supplier": supplier.id,
            "notes": "Loading labor",
        },
        format="json",
    )

    assert response.status_code == 201
    expense = Expense.objects.get(id=response.data["id"])
    assert expense.supplier == supplier


@pytest.mark.django_db
def test_expense_category_required_for_pure_expense(api_client, user, farm):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/v1/expenses/",
        {
            "amount": "120.00",
            "date": "2026-04-22",
            "notes": "Missing category",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_other_user_cannot_access_expense(api_client, other_user, farm):
    expense = Expense.objects.create(
        farm=farm,
        category="vet",
        amount=Decimal("250.00"),
        date="2026-04-20",
    )

    api_client.force_authenticate(user=other_user)
    response = api_client.get(f"/api/v1/expenses/{expense.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_list_expenses_returns_only_authenticated_users_records(
    api_client, user, other_user, farm, other_farm
):
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("100.00"),
        date="2026-04-20",
    )
    Expense.objects.create(
        farm=other_farm,
        category="vet",
        amount=Decimal("200.00"),
        date="2026-04-20",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/expenses/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["category"] == "feed"


# ----------------- Low Stock Tests -----------------
@pytest.mark.django_db
def test_low_stock_endpoint_returns_items_below_threshold(api_client, user, inventory_item):
    inventory_item.quantity_on_hand = Decimal("15.00")
    inventory_item.save()

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/inventory/low-stock/")

    assert response.status_code == 200
    returned_ids = [item["id"] for item in response.data]
    assert inventory_item.id in returned_ids


@pytest.mark.django_db
def test_low_stock_endpoint_excludes_items_above_threshold(api_client, user, inventory_item):
    inventory_item.quantity_on_hand = Decimal("100.00")
    inventory_item.save()

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/inventory/low-stock/")

    assert response.status_code == 200
    returned_ids = [item["id"] for item in response.data]
    assert inventory_item.id not in returned_ids


@pytest.mark.django_db
def test_low_stock_endpoint_excludes_items_with_no_threshold(api_client, user, farm):
    no_threshold_item = InventoryItem.objects.create(
        farm=farm,
        name="No Threshold Item",
        item_type="feed",
        unit="kg",
        quantity_on_hand=Decimal("0.00"),
        reorder_threshold=None,
        is_active=True,
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/inventory/low-stock/")

    assert response.status_code == 200
    returned_ids = [item["id"] for item in response.data]
    assert no_threshold_item.id not in returned_ids


# ----------------- Expense Summary Tests -----------------
@pytest.mark.django_db
def test_expense_summary_returns_total_and_breakdown(api_client, user, farm):
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("100.00"),
        date="2026-04-20",
    )
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("100.00"),
        date="2026-04-21",
    )
    Expense.objects.create(
        farm=farm,
        category="vet",
        amount=Decimal("200.00"),
        date="2026-04-22",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/expenses/summary/")

    assert response.status_code == 200
    assert response.data["total_spend"] == 400
    by_category = {item["category"]: item["total"] for item in response.data["by_category"]}
    assert by_category["feed"] == 200
    assert by_category["vet"] == 200


@pytest.mark.django_db
def test_expense_summary_filter_by_date_range(api_client, user, farm):
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("100.00"),
        date="2026-04-01",
    )
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("120.00"),
        date="2026-04-10",
    )
    Expense.objects.create(
        farm=farm,
        category="vet",
        amount=Decimal("200.00"),
        date="2026-04-20",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get(
        "/api/v1/expenses/summary/?start_date=2026-04-05&end_date=2026-04-15"
    )

    assert response.status_code == 200
    assert response.data["total_spend"] == 120


# ----------------- Service Unit Tests -----------------
@pytest.mark.django_db
def test_record_inventory_purchase_service_updates_quantity(farm, inventory_item):
    purchase = services.record_inventory_purchase(
        farm=farm,
        inventory_item=inventory_item,
        quantity=Decimal("50.00"),
        unit_cost=Decimal("10.00"),
        date="2026-04-20",
    )

    inventory_item.refresh_from_db()
    assert inventory_item.quantity_on_hand == Decimal("150.00")
    assert InventoryPurchase.objects.filter(id=purchase.id).exists()
    assert Expense.objects.filter(inventory_purchase=purchase).exists()


@pytest.mark.django_db
def test_record_inventory_usage_service_updates_quantity(farm, inventory_item):
    usage = services.record_inventory_usage(
        farm=farm,
        inventory_item=inventory_item,
        quantity_used=Decimal("30.00"),
        date="2026-04-21",
    )

    inventory_item.refresh_from_db()
    assert inventory_item.quantity_on_hand == Decimal("70.00")
    assert InventoryUsage.objects.filter(id=usage.id).exists()


@pytest.mark.django_db
def test_record_inventory_usage_service_raises_on_insufficient_stock(farm, inventory_item):
    with pytest.raises(ValidationError):
        services.record_inventory_usage(
            farm=farm,
            inventory_item=inventory_item,
            quantity_used=Decimal("150.00"),
            date="2026-04-21",
        )


@pytest.mark.django_db
def test_get_low_stock_items_service(farm, inventory_item):
    inventory_item.quantity_on_hand = Decimal("15.00")
    inventory_item.save()

    above_threshold = InventoryItem.objects.create(
        farm=farm,
        name="Above Threshold",
        item_type="feed",
        unit="kg",
        quantity_on_hand=Decimal("100.00"),
        reorder_threshold=Decimal("20.00"),
        is_active=True,
    )
    no_threshold = InventoryItem.objects.create(
        farm=farm,
        name="No Threshold",
        item_type="feed",
        unit="kg",
        quantity_on_hand=Decimal("0.00"),
        reorder_threshold=None,
        is_active=True,
    )

    queryset = services.get_low_stock_items(farm=farm)
    returned_ids = set(queryset.values_list("id", flat=True))

    assert inventory_item.id in returned_ids
    assert above_threshold.id not in returned_ids
    assert no_threshold.id not in returned_ids


@pytest.mark.django_db
def test_get_expense_summary_service(farm):
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("100.00"),
        date="2026-04-20",
    )
    Expense.objects.create(
        farm=farm,
        category="feed",
        amount=Decimal("150.00"),
        date="2026-04-20",
    )
    Expense.objects.create(
        farm=farm,
        category="vet",
        amount=Decimal("200.00"),
        date="2026-04-21",
    )

    queryset = Expense.objects.filter(farm=farm)
    result = services.get_expense_summary(queryset)

    assert result["total_spend"] == 450
    by_category = {item["category"]: item["total"] for item in result["by_category"]}
    assert by_category["feed"] == 250
    assert by_category["vet"] == 200
