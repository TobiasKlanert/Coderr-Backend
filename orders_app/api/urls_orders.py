from django.urls import path
"""
URL configuration for the orders API endpoints.

- The root path ('') is routed to OrderListCreateView and is intended to provide
    listing of orders (GET) and creation of new orders (POST).
- The detail path ('<int:pk>') is routed to OrderDetailView and is intended to
    provide retrieval, update, and deletion of a single order identified by its
    primary key (GET, PUT/PATCH, DELETE).
"""

from .views import OrderListCreateView, OrderDetailView


urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail')
]
