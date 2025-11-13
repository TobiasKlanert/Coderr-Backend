from django.urls import path
"""
URL configuration for the dashboard_app.api package.
This module exposes a single URL pattern that maps the module root ('')
to the DashboardOverviewView class-based view and names the route 'dashboard'.
"""
from .views import DashboardOverviewView
from django.urls import reverse

urlpatterns = [
    path('', DashboardOverviewView.as_view(), name='dashboard'),
]