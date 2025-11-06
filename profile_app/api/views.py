from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ProfileDetailSerializer, ProfileListSerializer
from ..models import UserProfile


class ProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user'

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()

        # Only allow the authenticated user to edit their own profile
        if request.user.id != profile.user_id:
            return Response(
                {"detail": "You can only edit your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update related User fields if provided
        user = request.user
        if "first_name" in request.data:
            user.first_name = request.data.get("first_name") or ""
        if "last_name" in request.data:
            user.last_name = request.data.get("last_name") or ""
        if "email" in request.data:
            user.email = request.data.get("email") or ""
        user.save()

        # Update profile fields if provided
        for field in ["location", "tel", "description", "working_hours"]:
            if field in request.data:
                setattr(profile, field, request.data.get(field) or "")
        profile.save()

        # Serialize and ensure specific fields are not null in the response
        data = self.get_serializer(profile).data
        for f in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(f) is None:
                data[f] = ""

        return Response(data, status=status.HTTP_200_OK)


class BusinessProfileListView(generics.ListAPIView):
    serializer_class = ProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (UserProfile.objects.filter(user__type='business')).distinct()


class CustomerProfileListView(generics.ListAPIView):
    serializer_class = ProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (UserProfile.objects.filter(user__type='customer')).distinct()
