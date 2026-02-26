from django.contrib import admin
from .models import MilkProduction


@admin.register(MilkProduction)
class MilkProductionAdmin(admin.ModelAdmin):
    list_display = ("cattle", "liters", "date_time", "created_at")
    list_filter = ("date_time", "cattle__farm")
    search_fields = ("cattle__tag_number",)
    ordering = ("-date_time",)
