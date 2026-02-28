from rest_framework import serializers
from apps.users.models import CustomUser
from .services import register_farm_owner

from apps.farms.models import Farm
from apps.farms.serializers import FarmSerializer
from django.db import IntegrityError


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    farm_name = serializers.CharField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        try:
            return register_farm_owner(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                "Registration failed due to a conflict. Please try a different username or email."
            )


class UserProfileSerializer(serializers.ModelSerializer):
    farms = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "role", "farms", "created_at"]
        read_only_fields = fields

    def get_farms(self, obj):
        """
        Returns a list of serialized farms for the user.
        Works whether user has a OneToOne or ForeignKey relationship.
        """
        # Try using related_name "farms" (ForeignKey)
        if hasattr(obj, "farms"):
            qs = obj.farms.all()
        # fallback for OneToOne "farm"
        elif hasattr(obj, "farm"):
            qs = [obj.farm] if obj.farm else []
        else:
            qs = []

        return FarmSerializer(qs, many=True).data