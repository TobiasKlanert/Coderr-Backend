from django.urls import path
from .views import BusinessProfileListView, CustomerProfileListView

urlpatterns = [
    path('business/', BusinessProfileListView.as_view(), name='profile-business-list'),
    path('customer/', CustomerProfileListView.as_view(), name='profile-customer-list'),
]

