from django.urls import path

from .views import OrderCompleteView


urlpatterns = [
    path('<int:pk>/', OrderCompleteView.as_view(), name='order-complete')
]