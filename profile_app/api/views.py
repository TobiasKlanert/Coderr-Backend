from rest_framework import generics, permissions
from .serializers import ProfileSerializer
from ..models import UserProfile

class ProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user'
