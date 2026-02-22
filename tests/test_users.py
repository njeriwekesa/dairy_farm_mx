from django.test import TestCase

def test_user_creation(user):
    assert user.email == "test@example.com"

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_registration():
    client = APIClient()

    response = client.post(
        "/api/users/register/",
        {
            "email": "farmer@example.com",
            "username": "farmer",
            "password": "StrongPass123",
            "farm_name": "My Dairy Farm"
        },
        format="json"
    )

    assert response.status_code == 201
