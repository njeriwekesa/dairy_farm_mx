from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
  email = models.EmailField(unique=True)

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["username"]

   # Optional role field for future use
  ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
  role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')

  # Timestamps
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.email
