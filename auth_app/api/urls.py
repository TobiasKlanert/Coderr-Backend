"""
URL configuration for the authentication API endpoints.

This module exposes the following API routes (used by the auth_app):
- registration/  : User registration endpoint (RegistrationView)
- login/         : Login endpoint (CustomLoginView) — returns auth token/session
"""

from django.urls import path
from .views import (
    RegistrationView,
    CustomLoginView,
    UserProfileRetrieveView,
    BusinessProfilesListView,
    CustomerProfilesListView,
)

urlpatterns = [
    # POST: create a new user account. Uses RegistrationView.as_view().
    path('registration/', RegistrationView.as_view(), name='registration'),

    # POST: authenticate user credentials and return a token.
    path('login/', CustomLoginView.as_view(), name='login'),

    # GET: user profile by id / PATCH: own user profile
    path('profile/<int:pk>/', UserProfileRetrieveView.as_view(), name='user-profile'),

    # GET: Lists of profiles by type
    path('profiles/business/', BusinessProfilesListView.as_view(), name='profiles-business'),
    path('profiles/customer/', CustomerProfilesListView.as_view(), name='profiles-customer'),
]
