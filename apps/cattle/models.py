from django.db import models
from django.conf import settings
from apps.farms.models import Farm


class Cattle(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="cattle"
    )

    tag_number = models.CharField(max_length=50)
    name = models.CharField(max_length=100, blank=True)
    breed = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("farm", "tag_number")
        ordering = ["-created_at"]
        verbose_name = "Cattle"
        verbose_name_plural = "Cattle"

    def __str__(self):
        return f"{self.tag_number} - {self.breed}"

