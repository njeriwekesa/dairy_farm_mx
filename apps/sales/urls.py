from rest_framework.routers import DefaultRouter

from .views import BuyerViewSet, SaleViewSet

router = DefaultRouter()
router.register(r"buyers", BuyerViewSet, basename="buyer")
router.register(r"sales", SaleViewSet, basename="sale")

urlpatterns = router.urls
