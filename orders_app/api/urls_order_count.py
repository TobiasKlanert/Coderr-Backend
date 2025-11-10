from django.urls import path

from .views import OrderCountView


urlpatterns = [
    path('<int:pk>/', OrderCountView.as_view(), name='order-count')
]