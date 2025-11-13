from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, filters
from rest_framework.permissions import IsAuthenticated

from .permissions import IsCustomerUser, IsReviewer
from .serializers import ReviewSerializer
from ..models import Review

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    APIView for listing existing Review instances and creating new ones.
    This view subclasses Django REST framework's ListCreateAPIView to provide:
    - GET: paginated list of reviews (authentication required).
    - POST: create a new review (authentication required and the creator must satisfy IsCustomerUser).
    Behavior and configuration:
    - queryset: Review.objects.all()
    - serializer_class: ReviewSerializer
    - Default permission_classes: IsAuthenticated (additional IsCustomerUser required for non-GET methods via get_permissions).
    - Filtering: enabled via DjangoFilterBackend; clients can filter by business_user_id and reviewer_id.
    - Searching and ordering: SearchFilter and OrderingFilter are enabled; allowed ordering fields are updated_at and rating.
    - On creation, perform_create() automatically assigns reviewer=self.request.user to the saved instance.
    Expected inputs:
    - For filtering: ?business_user_id=<id>&reviewer_id=<id>
    - For ordering: ?ordering=updated_at or ?ordering=-rating
    - For searching: dependent on serializer/search_fields configuration (SearchFilter enabled).
    Errors and responses:
    - 401 Unauthorized if the request is unauthenticated.
    - 403 Forbidden if an authenticated user lacks IsCustomerUser permission for write operations.
    - 400 Bad Request for serializer validation errors.
    """
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
    """
    Retrieve, update, or delete a single Review instance.
    This view is a DRF RetrieveUpdateDestroyAPIView configured to work with the Review model
    using ReviewSerializer. It exposes the following HTTP operations:
    - GET: Retrieve a serialized representation of a Review instance.
    - PATCH: Validate and update a Review instance; on successful update the instance's
        `updated_at` timestamp is set to django.utils.timezone.now() via perform_update.
    - DELETE: Remove a Review instance (delete delegates to the standard destroy() flow).
    Access control:
    - Requires authentication and that the requester satisfies the IsReviewer permission.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())