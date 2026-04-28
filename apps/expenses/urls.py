from rest_framework.routers import DefaultRouter

from .views import (
    ExpenseViewSet,
    InventoryItemViewSet,
    InventoryPurchaseViewSet,
    InventoryUsageViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"inventory", InventoryItemViewSet, basename="inventory")
router.register(r"inventory-purchases", InventoryPurchaseViewSet, basename="inventory-purchase")
router.register(r"inventory-usage", InventoryUsageViewSet, basename="inventory-usage")
router.register(r"expenses", ExpenseViewSet, basename="expense")

urlpatterns = router.urls
