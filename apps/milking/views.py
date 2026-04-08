from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateTimeFilter

from .models import MilkProduction
from .serializers import MilkProductionSerializer
from . import services


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

    filter_backends = [DjangoFilterBackend]
    filterset_class = MilkProductionFilter

    def get_queryset(self):
        return MilkProduction.objects.filter(
            cattle__farm__owner=self.request.user
        )

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        period = request.query_params.get("period", "total")

        if period == "daily":
            data = services.group_by_day(queryset)
        elif period == "weekly":
            data = services.group_by_week(queryset)
        elif period == "monthly":
            data = services.group_by_month(queryset)
        else:
            data = services.get_total_and_average(queryset)

        return Response(data)