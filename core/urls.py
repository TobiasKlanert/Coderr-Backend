from django.contrib import admin
"""
Core URL configuration for the Django project.

This module defines the top-level URL routes and delegates request handling to
application-level URLconfs. The configured routes include:

- 'admin/': Django admin interface.
- 'api/': Authentication and profile endpoints (delegates to auth_app.api.urls).
- 'api/offers/': Offers endpoints (delegates to offers_app.api.urls_offers).
- 'api/offerdetails/': Offer detail endpoints (delegates to offers_app.api.urls_details).
- 'api/orders/': Orders endpoints (delegates to orders_app.api.urls_orders).
- 'api/order-count/': Order count endpoints (delegates to orders_app.api.urls_order_count).
- 'api/completed-order-count/': Completed order count endpoints (delegates to orders_app.api.urls_order_completed).
- 'api/reviews/': Reviews endpoints (delegates to reviews_app.api.urls).
- 'api/base-info/': Dashboard base information endpoints (delegates to dashboard_app.api.urls).
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth and Profile endpoints
    path('api/', include('auth_app.api.urls')),
    # Offers endpoints
    path('api/offers/', include('offers_app.api.urls_offers')),
    # Offer-details endpoints
    path('api/offerdetails/', include('offers_app.api.urls_details')),
    # Orders endpoints
    path('api/orders/', include('orders_app.api.urls_orders')),
    path('api/order-count/', include('orders_app.api.urls_order_count')),
    path('api/completed-order-count/', include('orders_app.api.urls_order_completed')),
    # Review endpoints
    path('api/reviews/', include('reviews_app.api.urls')),
    # Dashboard endpoints
    path('api/base-info/', include('dashboard_app.api.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
