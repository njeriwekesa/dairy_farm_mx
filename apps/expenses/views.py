from django_filters.rest_framework import DateFilter, DjangoFilterBackend, FilterSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services
from .models import Expense, InventoryItem, InventoryPurchase, InventoryUsage, Supplier
from .serializers import (
    ExpenseSerializer,
    InventoryItemSerializer,
    InventoryPurchaseSerializer,
    InventoryUsageSerializer,
    SupplierSerializer,
)


class ExpenseFilter(FilterSet):
    start_date = DateFilter(field_name="date", lookup_expr="gte")
    end_date = DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Expense
        fields = ["category", "supplier", "start_date", "end_date"]


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Supplier.objects.filter(farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = self.request.user.farms.first()
        serializer.save(farm=farm)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Suppliers cannot be deleted. Set is_active=False to deactivate."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InventoryItem.objects.filter(farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = self.request.user.farms.first()
        serializer.save(farm=farm)

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        farm = request.user.farms.first()
        queryset = services.get_low_stock_items(farm)
        data = self.get_serializer(queryset, many=True).data
        return Response(data)


class InventoryPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InventoryPurchase.objects.filter(inventory_item__farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = self.request.user.farms.first()
        purchase = services.record_inventory_purchase(
            farm=farm,
            inventory_item=serializer.validated_data["inventory_item"],
            quantity=serializer.validated_data["quantity"],
            unit_cost=serializer.validated_data["unit_cost"],
            date=serializer.validated_data["date"],
        )
        serializer.instance = purchase


class InventoryUsageViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InventoryUsage.objects.filter(inventory_item__farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = self.request.user.farms.first()
        usage = services.record_inventory_usage(
            inventory_item=serializer.validated_data["inventory_item"],
            quantity_used=serializer.validated_data["quantity_used"],
            date=serializer.validated_data["date"],
        )
        serializer.instance = usage


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter

    def get_queryset(self):
        return Expense.objects.filter(farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = self.request.user.farms.first()
        expense = services.record_expense(
            farm=farm,
            category=serializer.validated_data.get("category"),
            amount=serializer.validated_data["amount"],
            date=serializer.validated_data["date"],
            supplier=serializer.validated_data.get("supplier"),
            inventory_item=serializer.validated_data.get("inventory_item"),
            notes=serializer.validated_data.get("notes", ""),
        )
        serializer.instance = expense

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = services.get_expense_summary(queryset)
        return Response(data)
