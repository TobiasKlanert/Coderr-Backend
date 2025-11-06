from django.contrib import admin
from .models import UserProfile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'type']
    list_filter = ['user__type']
    exclude = ['type']

    def first_name(self, obj):
        return obj.user.first_name
    first_name.admin_order_field = 'user__first_name'  # type: ignore[attr-defined]
    first_name.short_description = 'First name'  # type: ignore[attr-defined]

    def last_name(self, obj):
        return obj.user.last_name
    last_name.admin_order_field = 'user__last_name'  # type: ignore[attr-defined]
    last_name.short_description = 'Last name'  # type: ignore[attr-defined]

    def email(self, obj):
        return obj.user.email
    email.admin_order_field = 'user__email'  # type: ignore[attr-defined]
    email.short_description = 'Email'  # type: ignore[attr-defined]

    def type(self, obj):
        return obj.user.type
    type.admin_order_field = 'user__type'  # type: ignore[attr-defined]
    type.short_description = 'Type'  # type: ignore[attr-defined]


admin.site.register(UserProfile, ProfileAdmin)
