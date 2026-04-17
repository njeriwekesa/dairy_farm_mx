from django_filters.rest_framework import DateFilter, DjangoFilterBackend, FilterSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services
from .models import Buyer, Sale
from .serializers import BuyerSerializer, SaleSerializer


class SaleFilter(FilterSet):
    start_date = DateFilter(field_name="date", lookup_expr="gte")
    end_date = DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Sale
        fields = ["buyer", "buyer__buyer_type", "start_date", "end_date"]


class BuyerViewSet(viewsets.ModelViewSet):
    serializer_class = BuyerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Buyer.objects.filter(farm__owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Buyers cannot be deleted. Set is_active=False to deactivate."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SaleFilter

    def get_queryset(self):
        return Sale.objects.filter(farm__owner=self.request.user)

    def perform_create(self, serializer):
        sale = services.create_sale(
            farm=serializer.validated_data["farm"],
            buyer=serializer.validated_data["buyer"],
            liters_sold=serializer.validated_data["liters_sold"],
            price_per_litre=serializer.validated_data["price_per_litre"],
            date=serializer.validated_data["date"],
            notes=serializer.validated_data.get("notes", ""),
        )
        serializer.instance = sale

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = services.get_sales_summary(queryset)
        return Response(data)
