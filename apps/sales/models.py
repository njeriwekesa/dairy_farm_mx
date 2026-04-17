from django.db import models
from apps.farms.models import Farm


class Buyer(models.Model):
    class BuyerType(models.TextChoices):
        WALK_IN = "walk_in", "Walk In"
        B2B = "b2b", "B2B"

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="buyers",
    )
    name = models.CharField(max_length=255)
    buyer_type = models.CharField(max_length=20, choices=BuyerType.choices)
    contact = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("farm", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.farm.name})"


class Sale(models.Model):
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="sales",
    )
    buyer = models.ForeignKey(
        Buyer,
        on_delete=models.PROTECT,
        related_name="sales",
    )
    liters_sold = models.DecimalField(max_digits=6, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Sale #{self.id} - {self.liters_sold}L"
