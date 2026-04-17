from rest_framework import serializers

from .models import Buyer, Sale


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields["farm"].read_only = True
        return fields


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"
        read_only_fields = ("id", "created_at", "total_amount")

    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields["farm"].read_only = True
        return fields
