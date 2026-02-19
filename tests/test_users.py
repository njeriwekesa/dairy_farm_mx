from django.test import TestCase

def test_user_creation(user):
    assert user.email == "test@example.com"
