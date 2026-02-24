from rest_framework import serializers
from apps.users.models import CustomUser
from .services import register_farm_owner

from apps.farms.models import Farm
from apps.farms.serializers import FarmSerializer

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    farm_name = serializers.CharField()

    def create(self, validated_data):
        return register_farm_owner(validated_data)


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