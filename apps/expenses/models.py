from django.db import models

from apps.farms.models import Farm


class Supplier(models.Model):
    class SupplierType(models.TextChoices):
        WALK_IN = "walk_in", "Walk In"
        B2B = "b2b", "B2B"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="suppliers")
    name = models.CharField(max_length=255)
    supplier_type = models.CharField(max_length=20, choices=SupplierType.choices)
    contact = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("farm", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.farm.name})"


class InventoryItem(models.Model):
    class ItemType(models.TextChoices):
        FEED = "feed", "Feed"
        SUPPLEMENT = "supplement", "Supplement"
        VET = "vet", "Vet"
        LABOR = "labor", "Labor"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="inventory_items")
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    unit = models.CharField(max_length=50)
    quantity_on_hand = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reorder_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("farm", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.quantity_on_hand} {self.unit})"


class InventoryPurchase(models.Model):
    inventory_item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="purchases"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Purchase #{self.id} - {self.inventory_item.name}"


class InventoryUsage(models.Model):
    inventory_item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="usages"
    )
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Usage #{self.id} - {self.inventory_item.name}"


class Expense(models.Model):
    class Category(models.TextChoices):
        FEED = "feed", "Feed"
        SUPPLEMENT = "supplement", "Supplement"
        VET = "vet", "Vet"
        LABOR = "labor", "Labor"

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="expenses")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    inventory_purchase = models.OneToOneField(
        InventoryPurchase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expense",
    )
    category = models.CharField(max_length=20, choices=Category.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"Expense #{self.id} - {self.category}"
