from rest_framework import serializers
from .models import Cattle


class CattleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cattle
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def get_fields(self):
        fields = super().get_fields()

        # If instance exists, this is an update operation
        # Farm is read-only so it cannot be reassigned
        if self.instance:
            fields["farm"].read_only = True

        return fields