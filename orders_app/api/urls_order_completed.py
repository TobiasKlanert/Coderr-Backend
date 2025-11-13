from django.urls import path
"""
URL configuration for the "order complete" endpoint of the orders_app API.
This module exposes a single route that accepts an integer primary key for an order
and delegates request handling to OrderCompleteView.
"""

from .views import OrderCompleteView


urlpatterns = [
    path('<int:pk>/', OrderCompleteView.as_view(), name='order-complete')
]