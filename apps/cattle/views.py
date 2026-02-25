from rest_framework import viewsets, permissions
from .models import Cattle
from .serializers import CattleSerializer
from .permissions import IsFarmOwner
from rest_framework.exceptions import PermissionDenied


class CattleViewSet(viewsets.ModelViewSet):
    serializer_class = CattleSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmOwner]

    def get_queryset(self):
        return Cattle.objects.filter(farm__owner=self.request.user)

    def perform_create(self, serializer):
        farm = serializer.validated_data["farm"]

        if farm.owner != self.request.user:
            raise PermissionDenied("You do not own this farm.")

        serializer.save()

