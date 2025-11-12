from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, filters
from rest_framework.permissions import IsAuthenticated

from .permissions import IsCustomerUser, IsReviewer
from .serializers import ReviewSerializer
from ..models import Review

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
 
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsCustomerUser()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)