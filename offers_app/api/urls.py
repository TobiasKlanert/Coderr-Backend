from django.urls import path
from .views import OfferListCreateView, DetailRetrieveView

urlpatterns = [
    path('', OfferListCreateView.as_view(), name='offer-create'),
    path('offerdetails/<int:pk>/', DetailRetrieveView.as_view(), name='offer-detail'),
]
