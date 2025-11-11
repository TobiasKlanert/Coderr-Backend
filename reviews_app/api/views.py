from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .permissions import IsCustomerUser
from .serializers import ReviewSerializer
from ..models import Review

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsCustomerUser()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
