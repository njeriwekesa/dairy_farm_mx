from django.contrib import admin

from .models import Buyer, Sale


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "buyer_type", "is_active")
    list_filter = ("buyer_type", "is_active")
    search_fields = ("name", "farm__name")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "farm", "buyer", "liters_sold", "total_amount", "date")
    list_filter = ("date", "buyer__buyer_type")
    search_fields = ("buyer__name", "farm__name")
    ordering = ("-date", "-id")
