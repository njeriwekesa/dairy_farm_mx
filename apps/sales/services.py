from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError

from .models import Sale


def create_sale(farm, buyer, liters_sold, price_per_litre, date, notes=None):
    if buyer.farm_id != farm.id:
        raise ValidationError({"buyer": "Selected buyer does not belong to this farm."})

    total_amount = liters_sold * price_per_litre
    return Sale.objects.create(
        farm=farm,
        buyer=buyer,
        liters_sold=liters_sold,
        price_per_litre=price_per_litre,
        total_amount=total_amount,
        date=date,
        notes=notes or "",
    )


def get_sales_summary(queryset):
    totals = queryset.aggregate(
        total_sales=Count("id"),
        total_revenue=Coalesce(Sum("total_amount"), 0),
        total_liters_sold=Coalesce(Sum("liters_sold"), 0),
    )

    by_buyer_qs = (
        queryset.values("buyer_id", "buyer__name", "buyer__buyer_type")
        .annotate(
            total_liters=Coalesce(Sum("liters_sold"), 0),
            total_revenue=Coalesce(Sum("total_amount"), 0),
            sales_count=Count("id"),
        )
        .order_by("buyer__name")
    )

    by_buyer = [
        {
            "buyer_id": row["buyer_id"],
            "buyer_name": row["buyer__name"],
            "buyer_type": row["buyer__buyer_type"],
            "total_liters": row["total_liters"],
            "total_revenue": row["total_revenue"],
            "sales_count": row["sales_count"],
        }
        for row in by_buyer_qs
    ]

    return {
        "total_sales": totals["total_sales"],
        "total_revenue": totals["total_revenue"],
        "total_liters_sold": totals["total_liters_sold"],
        "by_buyer": by_buyer,
    }
