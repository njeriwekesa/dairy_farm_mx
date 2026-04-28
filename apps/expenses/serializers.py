from rest_framework import serializers

from .models import Expense, InventoryItem, InventoryPurchase, InventoryUsage, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ("id", "farm", "created_at")

    def validate_name(self, value):
        request = self.context.get("request")
        if request and not self.instance:
            farm = request.user.farms.first()
            if farm and Supplier.objects.filter(farm=farm, name=value).exists():
                raise serializers.ValidationError(
                    "A supplier with this name already exists for your farm."
                )
        return value


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = "__all__"
        read_only_fields = ("id", "farm", "quantity_on_hand", "created_at")


class InventoryPurchaseSerializer(serializers.ModelSerializer):
    farm = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InventoryPurchase
        fields = "__all__"
        read_only_fields = ("id", "total_cost", "created_at", "farm")

    def get_farm(self, obj):
        return obj.inventory_item.farm_id


class InventoryUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryUsage
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"
        read_only_fields = ("id", "farm", "created_at")

    def validate(self, attrs):
        inventory_item = attrs.get("inventory_item")
        category = attrs.get("category")
        if inventory_item is None and not category:
            raise serializers.ValidationError({"category": "This field is required."})
        return attrs
