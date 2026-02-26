from rest_framework.routers import DefaultRouter
from .views import MilkProductionViewSet

router = DefaultRouter()
router.register(r"milk", MilkProductionViewSet, basename="milk")

urlpatterns = router.urls