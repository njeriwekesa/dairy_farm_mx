from rest_framework import serializers
from apps.users.models import CustomUser
from .services import register_farm_owner

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    farm_name = serializers.CharField()

    def create(self, validated_data):
        return register_farm_owner(validated_data)
