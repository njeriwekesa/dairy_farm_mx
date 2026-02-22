from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer, UserProfileSerializer

# Register View
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "Farm owner registered successfully"},
            status=status.HTTP_201_CREATED
        )

# Profile View
class MeView(generics.RetrieveAPIView):
    """
    Returns the currently authenticated user's profile.
    Endpoint: GET /api/users/me/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user