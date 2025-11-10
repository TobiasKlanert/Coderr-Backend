from django.urls import path
from .views import OfferListCreateView, OfferDetailView

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-create'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]
