from rest_framework import serializers
from .models import Farm


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "location",
            "description",
            "established_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """
        Enforce one farm per user (for now).
        """
        user = self.context["request"].user

        if Farm.objects.filter(owner=user).exists():
            raise serializers.ValidationError(
                "You already have a registered farm."
            )

        return data

    def create(self, validated_data):
        """
        Automatically attach logged-in user as owner.
        """
        user = self.context["request"].user
        return Farm.objects.create(**validated_data)
