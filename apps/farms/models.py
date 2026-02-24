from django.db import models
from django.conf import settings

class Farm(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farms"
    )

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)

    description = models.TextField(blank=True)
    established_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.owner.email}"
