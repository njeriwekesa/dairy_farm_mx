from rest_framework import viewsets, permissions
from .models import Cattle
from .serializers import CattleSerializer
from .permissions import IsFarmOwner
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class CattleViewSet(viewsets.ModelViewSet):
    serializer_class = CattleSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["breed", "gender", "is_active"]
    search_fields = ["tag_number", "name"]
    ordering_fields = ["date_of_birth", "created_at"]

    def get_queryset(self):
        return Cattle.objects.filter(farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = serializer.validated_data["farm"]

        if farm.owner != self.request.user:
            raise PermissionDenied("You do not own this farm.")

        serializer.save()

