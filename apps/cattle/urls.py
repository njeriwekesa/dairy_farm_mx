from rest_framework.routers import DefaultRouter
from .views import CattleViewSet

router = DefaultRouter()
router.register(r"cattle", CattleViewSet, basename="cattle")

urlpatterns = router.urls
