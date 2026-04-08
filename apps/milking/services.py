from django.db.models import Sum, Avg
from datetime import timedelta


def get_total_and_average(queryset):
    """
    Returns total liters and average liters per record
    for a given MilkProduction queryset.
    """
    total = queryset.aggregate(total_liters=Sum("liters"))["total_liters"] or 0
    average = queryset.aggregate(avg_liters=Avg("liters"))["avg_liters"] or 0
    return {
        "total_liters": total,
        "average_liters_per_record": average,
    }


def group_by_day(queryset):
    """
    Returns total liters grouped by day.
    { "2026-02-27": 20.00, "2026-02-28": 9.00 }
    """
    records = queryset.order_by("date_time")
    groups = {}
    for record in records:
        key = record.date_time.date().isoformat()
        groups[key] = round(float(groups.get(key, 0)) + float(record.liters), 2)
    return groups


def group_by_week(queryset):
    """
    Returns total liters grouped by the Monday of each week.
    { "2026-02-23": 45.00 }
    """
    records = queryset.order_by("date_time")
    groups = {}
    for record in records:
        day = record.date_time.date()
        monday = day - timedelta(days=day.weekday())
        key = monday.isoformat()
        groups[key] = round(float(groups.get(key, 0)) + float(record.liters), 2)
    return groups


def group_by_month(queryset):
    """
    Returns total liters grouped by year-month.
    { "2026-02": 145.50 }
    """
    records = queryset.order_by("date_time")
    groups = {}
    for record in records:
        key = record.date_time.strftime("%Y-%m")
        groups[key] = round(float(groups.get(key, 0)) + float(record.liters), 2)
    return groups