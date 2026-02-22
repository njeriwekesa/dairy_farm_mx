from django.db import transaction
from apps.users.models import CustomUser
from apps.farms.models import Farm

#this ensures user + farm creation is atomic

@transaction.atomic
def register_farm_owner(validated_data):
    user = CustomUser.objects.create_user(
        email=validated_data["email"],
        username=validated_data["username"],
        password=validated_data["password"]
    )

    farm = Farm.objects.create(
        name=validated_data["farm_name"],
        owner=user
    )

    return user
