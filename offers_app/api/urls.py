from django.urls import path
from .views import OfferListCreateView, OfferDetailView, DetailRetrieveView

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-create'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', DetailRetrieveView.as_view(), name='details'),
]
