from django.urls import path
from .views import ProfileDetailView

urlpatterns = [
    # GET a specific user's profile by id | GET/PATCH the authenticated user's profile
    path('<int:user>/', ProfileDetailView.as_view(), name='profile-detail'),
]
