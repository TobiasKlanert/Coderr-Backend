from django.urls import path
from .views import ProfileDetailView

urlpatterns = [
    path('<int:user>/', ProfileDetailView.as_view(), name='profile-detail'),
]
