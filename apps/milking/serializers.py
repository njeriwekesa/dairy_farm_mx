from rest_framework import serializers
from .models import MilkProduction


class MilkProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkProduction
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    # Prevent recording milk for cattle you don't own
    def validate_cattle(self, value):
        request = self.context["request"]

        if value.farm.owner != request.user:
            raise serializers.ValidationError(
                "You cannot record milk for cattle you do not own."
            )
        return value

    # Prevent reassignment of milk record to another cow
    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields["cattle"].read_only = True
        return fields