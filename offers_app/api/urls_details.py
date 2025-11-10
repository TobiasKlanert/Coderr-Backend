from django.urls import path
from .views import DetailRetrieveView

urlpatterns = [
    path('<int:pk>/', DetailRetrieveView.as_view(), name='details'),
]