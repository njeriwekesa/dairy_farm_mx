from rest_framework import serializers
from .models import Buyer, Sale


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = "__all__"
        read_only_fields = ("id", "farm", "created_at")

    def validate_name(self, value):
        request = self.context.get("request")
        if request and not self.instance:
            farm = request.user.farms.first()
            if farm and Buyer.objects.filter(farm=farm, name=value).exists():
                raise serializers.ValidationError(
                    "A buyer with this name already exists for your farm."
                )
        return value


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"
        read_only_fields = ("id", "farm", "total_amount", "created_at")