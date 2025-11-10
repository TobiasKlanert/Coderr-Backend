from django.contrib import admin
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
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
