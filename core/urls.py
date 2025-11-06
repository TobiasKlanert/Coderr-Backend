from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth endpoints
    path('api/', include('auth_app.api.urls')),
    # Specific User profile
    path('api/profile/', include('profile_app.api.urls')),
    # Profiles collections (business/customer lists)
    path('api/profiles/', include('profile_app.api.profiles_urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
