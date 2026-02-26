from django.db import models
from apps.cattle.models import Cattle


class MilkProduction(models.Model):
    cattle = models.ForeignKey(
        Cattle,
        on_delete=models.CASCADE,
        related_name="milk_records"
    )
    date_time = models.DateTimeField(db_index=True)
    liters = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_time"]
        constraints = [
        models.UniqueConstraint(
            fields=["cattle", "date_time"],
            name="unique_milk_record_per_session"
        )
    ]

    def __str__(self):
        return f"{self.cattle.tag_number} - {self.liters}L"