from decimal import Decimal

from django.db import models
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError

from .models import Expense, InventoryPurchase, InventoryUsage


def record_expense(
    farm,
    amount,
    date,
    category=None,
    supplier=None,
    inventory_item=None,
    inventory_purchase=None,
    notes=None,
):
    if inventory_item is not None:
        category = inventory_item.item_type
    elif not category:
        raise ValidationError({"category": "This field is required for non-inventory expenses."})

    return Expense.objects.create(
        farm=farm,
        supplier=supplier,
        inventory_item=inventory_item,
        inventory_purchase=inventory_purchase,
        category=category,
        amount=amount,
        date=date,
        notes=notes or "",
    )


def record_inventory_purchase(farm, inventory_item, quantity, unit_cost, date, notes=None):
    if inventory_item.farm_id != farm.id:
        raise ValidationError({"inventory_item": "Selected item does not belong to this farm."})

    total_cost = quantity * unit_cost
    purchase = InventoryPurchase.objects.create(
        inventory_item=inventory_item,
        quantity=quantity,
        unit_cost=unit_cost,
        total_cost=total_cost,
        date=date,
    )

    inventory_item.quantity_on_hand += quantity
    inventory_item.save(update_fields=["quantity_on_hand"])

    record_expense(
        farm=farm,
        amount=total_cost,
        date=date,
        supplier=None,
        inventory_item=inventory_item,
        inventory_purchase=purchase,
        notes=notes or "",
    )

    return purchase


def record_inventory_usage(inventory_item, quantity_used, date, farm=None):
    if farm is not None and inventory_item.farm_id != farm.id:
        raise ValidationError({"inventory_item": "Selected item does not belong to this farm."})
    if quantity_used > inventory_item.quantity_on_hand:
        raise ValidationError({"quantity_used": "Insufficient stock on hand."})

    usage = InventoryUsage.objects.create(
        inventory_item=inventory_item,
        quantity_used=quantity_used,
        date=date,
    )

    inventory_item.quantity_on_hand -= quantity_used
    inventory_item.save(update_fields=["quantity_on_hand"])
    return usage


def get_low_stock_items(farm):
    return farm.inventory_items.filter(
        reorder_threshold__isnull=False,
        quantity_on_hand__lte=models.F("reorder_threshold"),
    )


def get_expense_summary(queryset):
    zero = Value(Decimal("0"), output_field=DecimalField())

    totals = queryset.aggregate(total_spend=Coalesce(Sum("amount"), zero))

    by_category_qs = (
        queryset.values("category")
        .annotate(total=Coalesce(Sum("amount"), zero), count=Count("id"))
        .order_by("category")
    )
    by_supplier_qs = (
        queryset.filter(supplier__isnull=False)
        .values("supplier_id", "supplier__name")
        .annotate(total=Coalesce(Sum("amount"), zero), count=Count("id"))
        .order_by("supplier__name")
    )

    return {
        "total_spend": totals["total_spend"],
        "by_category": [
            {"category": row["category"], "total": row["total"], "count": row["count"]}
            for row in by_category_qs
        ],
        "by_supplier": [
            {
                "supplier_id": row["supplier_id"],
                "supplier_name": row["supplier__name"],
                "total": row["total"],
                "count": row["count"],
            }
            for row in by_supplier_qs
        ],
    }
