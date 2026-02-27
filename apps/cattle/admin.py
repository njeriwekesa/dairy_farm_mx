from django.contrib import admin
from .models import Cattle

@admin.register(Cattle)
class CattleAdmin(admin.ModelAdmin):
    list_display = ("tag_number", "farm")
    search_fields = ("tag_number",)
