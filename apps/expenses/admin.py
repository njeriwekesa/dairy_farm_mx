from django.contrib import admin

from .models import Expense, InventoryItem, InventoryPurchase, InventoryUsage, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "supplier_type", "is_active")
    list_filter = ("supplier_type", "is_active")
    search_fields = ("name", "farm__name")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "farm", "item_type", "unit", "quantity_on_hand", "reorder_threshold")
    list_filter = ("item_type", "is_active")
    search_fields = ("name", "farm__name")


@admin.register(InventoryPurchase)
class InventoryPurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "inventory_item", "quantity", "unit_cost", "total_cost", "date")
    list_filter = ("date",)
    search_fields = ("inventory_item__name",)


@admin.register(InventoryUsage)
class InventoryUsageAdmin(admin.ModelAdmin):
    list_display = ("id", "inventory_item", "quantity_used", "date")
    list_filter = ("date",)
    search_fields = ("inventory_item__name",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "farm", "category", "amount", "supplier", "date")
    list_filter = ("category", "date")
    search_fields = ("farm__name", "supplier__name", "inventory_item__name")
