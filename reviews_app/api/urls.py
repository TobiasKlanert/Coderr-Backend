from django.urls import path
"""
URL configuration for the reviews_app.api module.
Defines two URL patterns that map to class-based views handling review resources:
- '' (name='review')
    Maps to ReviewListCreateView. Intended to provide an endpoint for:
        - listing reviews (GET)
        - creating a new review (POST)
- '<int:pk>/' (name='review-detail')
    Maps to ReviewDetailView. Intended to provide an endpoint for operations on
    a single review identified by its integer primary key `pk`, such as:
        - retrieving a review (GET)
        - updating a review (PATCH)
        - deleting a review (DELETE)
"""
from .views import ReviewListCreateView, ReviewDetailView

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail')
]