from django.urls import path
"""
Defines URL routing for the order count endpoint used by the orders_app API.
"""

from .views import OrderCountView
from django.urls import reverse


urlpatterns = [
    path('<int:pk>/', OrderCountView.as_view(), name='order-count')
]