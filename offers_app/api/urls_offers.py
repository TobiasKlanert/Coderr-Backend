from django.urls import path
"""
URL route definitions for the offers API.

This module declares two URL patterns that route HTTP requests to class-based views
which manage "offer" resources:

- '' (name='offer-create')
    - Mapped view: OfferListCreateView
    - Usage:
        * GET  -> list offers
        * POST -> create a new offer

- '<int:pk>/' (name='offer-detail')
    - Mapped view: OfferDetailView
    - Usage:
        * GET        -> retrieve a specific offer by primary key
        * PUT/PATCH  -> update the offer
        * DELETE     -> delete the offer
    - Uses Django's path converter <int:pk> to capture the offer ID.
"""
from .views import OfferListCreateView, OfferDetailView

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-create'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]
