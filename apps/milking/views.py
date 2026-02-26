from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MilkProduction
from .serializers import MilkProductionSerializer


class MilkProductionViewSet(viewsets.ModelViewSet):
    serializer_class = MilkProductionSerializer
    permission_classes = [IsAuthenticated]

    # Multi-tenant filtering
    def get_queryset(self):
        return MilkProduction.objects.filter(
            cattle__farm__owner=self.request.user
        )

    # Aggregation endpoint (MVP )
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.get_queryset()

        total = queryset.aggregate(total_liters=Sum("liters"))
        average = queryset.aggregate(avg_liters=Avg("liters"))

        return Response({
            "total_liters": total["total_liters"] or 0,
            "average_liters_per_record": average["avg_liters"] or 0,
        })
