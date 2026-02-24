from rest_framework import viewsets, permissions
from .models import Farm
from .serializers import FarmSerializer


class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own farm(s).
        """
        return Farm.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Attach logged-in user as owner automatically.
        """
        serializer.save(owner=self.request.user)
