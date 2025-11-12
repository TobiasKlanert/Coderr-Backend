from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail')
]