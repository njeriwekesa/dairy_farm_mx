from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateTimeFilter

from .models import MilkProduction
from .serializers import MilkProductionSerializer


# Custom FilterSet for MilkProduction
class MilkProductionFilter(FilterSet):
    start_date = DateTimeFilter(field_name="date_time", lookup_expr="gte")
    end_date = DateTimeFilter(field_name="date_time", lookup_expr="lte")

    class Meta:
        model = MilkProduction
        fields = ["cattle__tag_number", "start_date", "end_date"]


# ViewSet with ownership filtering and filtering backend
class MilkProductionViewSet(viewsets.ModelViewSet):
    serializer_class = MilkProductionSerializer
    permission_classes = [IsAuthenticated]

    # Enable DjangoFilterBackend and attach our custom filter
    filter_backends = [DjangoFilterBackend]
    filterset_class = MilkProductionFilter

    def get_queryset(self):
        # Only return milk records belonging to the logged-in user's farm(s)
        return MilkProduction.objects.filter(
            cattle__farm__owner=self.request.user
        )

    # Aggregation endpoint (MVP) with respect to filtering
    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())  # respect filtering params
        total = queryset.aggregate(total_liters=Sum("liters"))
        average = queryset.aggregate(avg_liters=Avg("liters"))

        return Response({
            "total_liters": total["total_liters"] or 0,
            "average_liters_per_record": average["avg_liters"] or 0,
        })