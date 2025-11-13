from django.urls import path
"""
URL configuration for the offers_app detail endpoint.
This module registers a single URL pattern that maps an integer primary-key
segment to a view responsible for returning a single resource's details.
"""
from .views import DetailRetrieveView

urlpatterns = [
    path('<int:pk>/', DetailRetrieveView.as_view(), name='details'),
]